# ------------------ Imports ------------------
from flask import (
    Blueprint, render_template, url_for,
    redirect, request
)
from flask_login import confirm_login
from flask_mail import Message
from ProjectsWebsite.database.models import User, Article, Blacklist, user_datastore
from ProjectsWebsite.forms import AccountManegementForms
from ProjectsWebsite.util import (scrapeError as _scrapeError,
                                  token_auth_required, generate_err_request_url,
                                  logout_user, roles_required, unverfiedLogUtil
                                  )
from ProjectsWebsite.util.mail import defaultMail, blacklistMail
from ProjectsWebsite.modules import db, guard, mail
from functools import partial

# ------------------ Blueprint Config ------------------
admin = Blueprint('admin', __name__, static_folder='static', template_folder='templates', url_prefix='/admin')

# ------------------ Blueprint Routes ------------------
@admin.route('/')
@roles_required('admin')
@token_auth_required
def adminRedirectHomePage():
    """
    Administrator Redirect to Homepage
    """
    confirm_login()
    return redirect(url_for("admin.adminHomePage"))

@admin.route('/dashboard')
@admin.route('/dashboard/')
@roles_required('admin')
@token_auth_required
def adminHomePage():
    """
    Administrator Homepage
    """
    confirm_login()
    return render_template('private/admin/index.html')

@admin.route('/manegement/accounts/', methods=['GET', 'POST'], defaults={'page': 1})
@admin.route('/manegement/accounts/<int:page>', methods=['GET', 'POST'])
@roles_required('admin')
@token_auth_required
def adminAccountsManegement(page):
    """
    Administrator Account Manegement page
    """
    search_form = AccountManegementForms.tableSearchForm()
    page = page
    pages = 3
    users = User.query.paginate(page, pages, error_out=False)
    if request.method == 'POST':
        form_found = False
        while not form_found:
            if not isinstance(search_form.command.data, type(None)) or search_form.command.data != "":
                search_query = search_form.command.data
                form_found = True
        if search_query:
            users = User.query.filter(User.name.like(search_query)).paginate(per_page=pages, error_out=False)
        else:
            users = User.query.paginate(page, pages, error_out=False)
    return render_template("private/admin/accounts.html", accounts=users, tbl_search_form=search_form)

@admin.route('management/accounts/edit_user/<string:user>/', methods=['GET', 'POST'], defaults={'page': 1})
@admin.route('management/accounts/edit_user/<string:user>/<int:page>', methods=['GET', 'POST'])
@admin.route('management/accounts/edit_user/<string:user>/<action>/<item_id>/<int:page>', methods=['GET', 'POST'])
@token_auth_required
def adminAccountsUserManagement(user, page, action=None, item_id=None):
    page: int = page
    pages = 3
    user = str(user).replace('%20', ' ')
    user_info = User.lookup_by_name(user)
    if user_info.is_blacklisted:
        blacklist_info = Blacklist.query.filter_by(blacklisted_person=user_info.name).first()
    else:
        blacklist_info = None
    URL = generate_err_request_url(in_admin_acc_edit_page=True, account_name=user)
    scrapeError = partial(_scrapeError, URL, 'p', auth=True)
    info_forms, search_form, role_form, delete_role_forms, delete_article_forms, ext_options = (
        AccountManegementForms.adminUserInfoForm(), AccountManegementForms.tableSearchForm(), 
        AccountManegementForms.roleForm(), AccountManegementForms.roleForm.deleteRoleTableForms(),
        AccountManegementForms.ArticleDeleteForms(), AccountManegementForms.extOptionForm()
    )
    article_info = Article.query.filter(Article.author.like(user)).paginate(page, pages, error_out=False)
    action = request.args.get("action")
    if request.method == "POST":
        if info_forms.name.data and info_forms.name.validate(info_forms):
            user_info.name = info_forms.name.data
            user = info_forms.name.data
        elif not info_forms.name.validate(info_forms) and info_forms.name.data:
            name_error = scrapeError(('id', 'name-err-p'), info_forms.name.errors)
        elif info_forms.email.data and info_forms.email.validate(info_forms):
            user_info.email = info_forms.email.data
        elif not info_forms.email.validate(info_forms) and info_forms.email.data:
            email_error = scrapeError(('id', 'email-err-p'), info_forms.email.data)
        elif info_forms.password.data and info_forms.password.validate(info_forms):
            user_info.hashed_password = guard.hash_password(info_forms.password.data)
        elif not info_forms.password.validate(info_forms) and info_forms.password.data:
            password_error = scrapeError(('id', 'pwd-err-p'), info_forms.password.errors)
        elif info_forms.active.data and info_forms.active.validate(info_forms):
            if info_forms.active.data == "False":
                data = False
                logout_user()
            else:
                data = True
            user_info.active = data
            db.session.commit()
        elif not info_forms.active.validate(info_forms) and info_forms.active.data:
            active_error = scrapeError(('id', 'active-status-err-p'), info_forms.active.errors)
        elif role_form.delete_all.data:
            for role in user_info.roles:
                if role not in ('admin', 'verified', 'unverified'):
                    user_datastore.remove_role_from_user(user_info, role)
                    user_datastore.commit()
        elif role_form.add_role.data and role_form.add_role.validate(role_form):
            user_datastore.add_role_to_user(user_info, role_form.add_role.data)
            user_datastore.commit()
        elif not role_form.add_role.validate(role_form) and role_form.add_role.data:
            add_role_error = scrapeError(('id', 'add-role-err-p'), role_form.add_role.errors)
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
        elif search_form.command.data and search_form.command_sbmt.data:
            search_query = search_form.command.data
            article_info = Article.query.filter(Article.title.like(search_query)).paginate(per_page=pages, error_out=False)
            for article in article_info.items:
                if article.author != user_info.name:
                    article_info.items.remove(article)
        elif delete_article_forms.delete_article.data:
            if action == "delete":
                item_id = request.args.get("item_id")
                Article.delete(item_id)
                user_datastore.commit()
        elif delete_article_forms.delete_all.data:
            Article.delete_all(user_info.name)
            user_datastore.commit()
        elif ext_options.blacklist.data: 
            reason = ext_options.reason.data
            user_id = user_info.id
            try:
                reasons = list(reason.split("|"))
            except Exception:
                reasons = []
            blacklist_msg = Message('Ban Notice', recipients=[user_info.username])
            blacklist_msg.html = blacklistMail(user_info.name, user_id, reasons)
            mail.send(blacklist_msg)
            print("past mail section")
            if reasons == []:
                reason_list = "No Reasons"
            else:
                reason_list = ""
                for reason in reasons:
                    reason_list += f"- {reason}\n"
            blacklist_query = Blacklist.add_blacklist(
                blacklisted_person=user_info.name,
                reason=reason_list
            )
            user_info.blacklisted = True
            user_datastore.put(blacklist_query)
            user_datastore.commit()
        elif ext_options.unblacklist.data: ...
        return redirect(url_for(".adminAccountsUserManagement", user=user_info.name))
    else:
        return render_template("private/admin/accountsuser.html", user=user_info, article_info=article_info, search_form=search_form, info_forms=info_forms, 
                               role_form=role_form, delete_role_forms=delete_role_forms, delete_article_forms=delete_article_forms, ext_options=ext_options)
        