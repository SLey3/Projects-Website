# ------------------ Imports ------------------
from flask import (
    Blueprint, render_template, url_for,
    redirect, request
)
from flask_login import login_required, confirm_login
from flask_security import roles_required
from src.database.models import User, Article
from src.forms import AccountManegementForms
from src.util.helpers import bool_re, email_re

# ------------------ Blueprint Config ------------------
admin = Blueprint('admin', __name__, static_folder='static', template_folder='templates/private/', url_prefix='/admin')

# ------------------ Blueprint Routes ------------------
@admin.route('/')
@login_required
@roles_required('admin', 'verified')
def adminRedirectHomePage():
    """
    Administrator Redirect to Homepage
    """
    confirm_login()
    return redirect(url_for("admin.adminHomePage"))

@admin.route('/dashboard')
@admin.route('/dashboard/')
@login_required
@roles_required('admin', 'verified')
def adminHomePage():
    """
    Administrator Homepage
    """
    confirm_login()
    return render_template('admin/index.html')

@admin.route('/manegement/accounts/', methods=['GET', 'POST'], defaults={'page': 1})
@admin.route('/manegement/accounts/<int:page>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'verified')
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
    return render_template("admin/accounts.html", accounts=users, tbl_search_form=search_form)


@admin.route('management/accounts/edit_user/<string:user>/', methods=['GET', 'POST'], defaults={'page':1})
@admin.route('management/accounts/edit_user/<string:user>/<int:page>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'verified')
def adminAccountsUserManagement(user, page):
    search_form = AccountManegementForms.tableSearchForm()
    info_forms= AccountManegementForms.adminUserInfoForm()
    page: int = page
    pages = 3
    user = str(user).replace('%20', ' ')
    user_info = User.query.filter_by(name=user).first()
    article_info = Article.query.filter(Article.author.like(user)).paginate(page, pages, error_out=False)
    return render_template("admin/accountsuser.html", user=user_info, article_info=article_info, search_form=search_form, info_forms=info_forms)

@admin.route('management/accounts/edit_user/<string:user>/post_form', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'verified')
def adminAccountsUserManagementformValidations(user):
    if request.method == "POST":
        return redirect(url_for("admin.adminAccountsUserManagement", user=user))
    else:
        return redirect(url_for("admin.adminAccountsUserManagement", user=user))
        