# ------------------ Imports ------------------
from flask import (
    Blueprint,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import confirm_login
from flask_mail import Message
from marshmallow import fields
from sqlalchemy.exc import OperationalError

try:
    from ProjectsWebsite.database.models import Article, Blacklist, User, user_datastore
    from ProjectsWebsite.database.models.roles import Roles
    from ProjectsWebsite.database.models.schemas import AccountUserManagementWebArgs
    from ProjectsWebsite.forms import AccountManegementForms
    from ProjectsWebsite.modules import db, guard, mail
    from ProjectsWebsite.util import (
        InternalError_or_success,
        MultipleFormsConfig,
        QueryLikeSearch,
        countSQLItems,
        logout_user,
        makeResultsObject,
        roles_required,
    )
    from ProjectsWebsite.util import temp_save as _temp_save
    from ProjectsWebsite.util import (
        token_auth_required,
        unverfiedLogUtil,
        validate_multiple_forms,
    )
    from ProjectsWebsite.util.mail import blacklistMail, defaultMail, unBlacklistMail
    from ProjectsWebsite.util.parsers.webargs import EditProfUrlParser
except ModuleNotFoundError:
    from .database.models import Article, Blacklist, User, user_datastore
    from .database.models.roles import Roles
    from .database.models.schemas import AccountUserManagementWebArgs
    from .forms import AccountManegementForms
    from .modules import db, guard, mail
    from .util import (
        InternalError_or_success,
        QueryLikeSearch,
        countSQLItems,
        logout_user,
        makeResultsObject,
        roles_required,
    )
    from .util import temp_save as _temp_save
    from .util import token_auth_required, unverfiedLogUtil, validate_multiple_forms
    from .util.mail import blacklistMail, defaultMail, unBlacklistMail
    from .util.parsers.webargs import EditProfUrlParser

# ------------------ Blueprint Config ------------------
admin = Blueprint(
    "admin",
    __name__,
    static_folder="static",
    template_folder="templates",
    url_prefix="/admin",
)

temp_save = _temp_save()

parser = EditProfUrlParser({"actions": _temp_save(), "page": 1})

# ------------------ Blueprint Routes ------------------
@admin.route("/")
@roles_required(Roles.ADMIN, Roles.VERIFIED)
@token_auth_required
def adminRedirectHomePage():
    """
    Administrator Redirect to Homepage
    """
    confirm_login()
    return redirect(url_for("admin.adminHomePage"))


@admin.route("/dashboard")
@admin.route("/dashboard/")
@roles_required(Roles.ADMIN, Roles.VERIFIED)
@token_auth_required
def adminHomePage():
    """
    Administrator Homepage
    """
    confirm_login()
    return render_template("private/admin/index.html")


@admin.route("/manegement/accounts/", methods=["GET", "POST"])
@parser.use_args({"page": fields.Int()}, location="query")
@roles_required(Roles.ADMIN, Roles.VERIFIED)
@token_auth_required
def adminAccountsManegement(args):
    """
    Administrator Account Manegement page
    """
    search_form = AccountManegementForms.tableSearchForm()
    page = args["page"]
    pages = 3
    users = User.query.paginate(page, pages, error_out=False)
    users = makeResultsObject(users)
    if request.method == "POST":
        if search_form.command.data:
            users = QueryLikeSearch("User", search_form.command.data, page, pages)
    return render_template(
        "private/admin/accounts.html", accounts=users, tbl_search_form=search_form
    )


@admin.route(
    "management/accounts/edit_user/process_blacklist/<string:client>", methods=["POST"]
)
def adminAccountsUserManagementProcessBlacklist(client):
    user_name = request.form["user"] or client
    if "%20" in user_name:
        user_name = user_name.replace("%20", " ")
    if user_name:
        user_info = User.lookup_by_name(user_name)
        if request.form["type"] == "blacklist":
            reason = request.form.get("reasons", None)
            user_id = str(user_info.id)
            if reason:
                reasons = list(reason.split("|"))
            else:
                reasons = "No Reasons"
            blacklist_msg = Message("Ban Notice", recipients=[user_info.username])
            blacklist_msg.html = blacklistMail(user_info.name, user_id, reasons)
            mail.send(blacklist_msg)
            if reasons == "No Reasons":
                reason_list = "No Reasons"
            else:

                reason_list = "<br>"
                for reason in reasons:
                    reason_list += f"- {reason} <br>"
            blacklist_query = Blacklist.add_blacklist(
                name=user_info.name, reason=reason_list
            )
            user_info.blacklisted = True
            user_datastore.put(blacklist_query)
            user_datastore.commit()
            # logout_user()
        elif request.form["type"] == "unBlacklist":
            reason = request.form.get("reasons", None)
            if reason:
                reasons = list(reason.split("|"))
            else:
                reasons = "No Reasons"
            unblacklist_msg = Message("Unban Notice", recipients=[user_info.username])
            unblacklist_msg.html = unBlacklistMail(user_info.name, reasons)
            mail.send(unblacklist_msg)
            Blacklist.remove_blacklist(user_info.name)
            user_info.blacklisted = False
            user_datastore.commit()
            Blacklist.query.filter_by(name=user_info.name).first()
        return jsonify({"reasons": reason})


@admin.route("management/accounts/edit_user/process_search/", methods=["POST"])
def adminAccountsUserManagementProcessSearch():
    ajax_data = request.form["search_data"] or None
    user = User.lookup_by_name(temp_save["user"])
    page = temp_save["page"]
    pages = temp_save["total_pages"]
    if pages == 1:
        pages = pages + page
    if ajax_data:
        article_info = QueryLikeSearch(
            "Article", ajax_data, page, pages, user.name, "title"
        )
    else:
        article_info = QueryLikeSearch("Article", None, page, pages, user.name)
    return render_template(
        "private/admin/render/_search_ajax.html",
        article_info=article_info,
        user=user,
        delete_article_forms=AccountManegementForms.ArticleDeleteForms(),
    )


@admin.route("management/accounts/edit_user/", methods=["GET", "POST"])
@parser.use_args(AccountUserManagementWebArgs(), location="querystring")
@token_auth_required
def adminAccountsUserManagement(args):
    page = args["page"]
    action = args["actions"]["action"]
    item_id = args["actions"]["item_id"]
    user = args["user"].replace("%20", " ").replace("+", " ")
    article_pages = page + countSQLItems("Article")
    temp_save.setMultipleValues(
        ("total_pages", "page", "user"), [article_pages, page, user]
    )
    user_info = User.lookup_by_name(user)
    with InternalError_or_success((AttributeError,), True):
        if user_info.is_blacklisted:
            blacklist_info = Blacklist.query.filter_by(name=user_info.name).first()
        else:
            blacklist_info = None
    (
        info_forms,
        search_form,
        role_form,
        delete_role_forms,
        delete_article_forms,
        ext_options,
    ) = (
        AccountManegementForms.adminUserInfoForm(),
        AccountManegementForms.tableSearchForm(),
        AccountManegementForms.roleForm(),
        AccountManegementForms.roleForm.deleteRoleTableForms(),
        AccountManegementForms.ArticleDeleteForms(),
        AccountManegementForms.extOptionForm(),
    )
    with InternalError_or_success(OperationalError):
        article_info = QueryLikeSearch(
            "Article", None, page, article_pages, user_info.name
        )
    action = request.args.get("action")
    _validate_mutiple_forms_config = MultipleFormsConfig(
        [
            info_forms,
            role_form,
            search_form,
            role_form,
            delete_role_forms,
            delete_article_forms,
        ],
        [
            ["name", "email", "password", "active"],
            ["command", "command_sbmt"],
            "add_role",
            ["member_field", "verified_field", "unverified_field", "editor_field"],
            ["delete_article"],
        ],
        [
            ["name", "email", "password", "active"],
            [],
            ["add_role"],
            ["member_field", "verified_field", "unverified_field", "editor_field"],
            ["delete_article"],
        ],
        [False, True, False, False, False],
    )
    if request.method == "POST" and validate_multiple_forms(
        _validate_mutiple_forms_config
    ):
        print("IN POST METHOD")
        print(info_forms.email.data)
        print(info_forms.email.errors)
        print(info_forms.email_sbmt.data)
        if info_forms.name.data:
            user_info.name = info_forms.name.data
            user = info_forms.name.data
        elif info_forms.email_sbmt.data:
            user_info.username = info_forms.email.data
            user_datastore.commit()
        elif info_forms.password.data:
            user_info.hashed_password = guard.hash_password(info_forms.password.data)
        elif info_forms.active.data:
            if info_forms.active.data == "False":
                data = False
                logout_user()
            else:
                data = True
            user_info.active = data
            db.session.commit()
        elif role_form.delete_all.data:
            for role in user_info.iter_roles():
                if role not in ("admin", "verified", "unverified"):
                    user_datastore.remove_role_from_user(user_info, role)
                    user_datastore.commit()
        elif role_form.add_role.data:
            role = getattr(Roles, role_form.add_role.data.upper())
            user_datastore.add_role_to_user(user_info, role)
            user_datastore.commit()
        elif delete_role_forms.member_field.data:
            user_datastore.remove_role_from_user(user_info, "member")
            user_datastore.commit()
        elif delete_role_forms.verified_field.data:
            user_datastore.remove_role_from_user(user_info, "verified")
            user_datastore.commit()
        elif delete_role_forms.unverified_field.data:
            user_datastore.remove_role_from_user(user_info, "unverified")
            user_datastore.commit()
            log = unverfiedLogUtil()
            log.removeContent(user_info.username)
        elif delete_role_forms.editor_field.data:
            user_datastore.remove_role_from_user(user_info, "editor")
            user_datastore.commit()
        elif delete_article_forms.delete_article.data:
            if action == "delete":
                Article.delete(item_id)
                user_datastore.commit()
        elif delete_article_forms.delete_all.data:
            Article.delete_all(user_info.name)
            user_datastore.commit()
        return redirect(url_for(".adminAccountsUserManagement", user=user_info.name))
    else:
        return render_template(
            "private/admin/accountsuser.html",
            user=user_info,
            article_info=article_info,
            search_form=search_form,
            info_forms=info_forms,
            role_form=role_form,
            delete_role_forms=delete_role_forms,
            delete_article_forms=delete_article_forms,
            ext_options=ext_options,
            blacklist_info=blacklist_info,
        )
