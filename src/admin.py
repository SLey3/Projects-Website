# ------------------ Imports ------------------
from flask import (
    Blueprint, render_template, url_for,
    redirect, request
)
from src.database.models import db
from flask_login import login_required, confirm_login
from flask_security import roles_required
from src.database.models import User, Article
from src.forms import AccountManegementForms
from src.util import scrapeError
from passlib.hash import sha512_crypt
from bs4 import BeautifulSoup, NavigableString
from typing import Union
import requests

# ------------------ Blueprint Config ------------------
admin = Blueprint('admin', __name__, static_folder='static', template_folder='templates', url_prefix='/admin')

# ------------------ Blueprint Routes ------------------
@admin.route('/')
def adminRedirectHomePage():
    """
    Administrator Redirect to Homepage
    """
    confirm_login()
    return redirect(url_for("admin.adminHomePage"))

@admin.route('/dashboard')
@admin.route('/dashboard/')
def adminHomePage():
    """
    Administrator Homepage
    """
    confirm_login()
    return render_template('private/admin/index.html')

@admin.route('/manegement/accounts/', methods=['GET', 'POST'], defaults={'page': 1})
@admin.route('/manegement/accounts/<int:page>', methods=['GET', 'POST'])
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


@admin.route('management/accounts/edit_user/<string:user>/', methods=['GET', 'POST'], defaults={'page':1})
@admin.route('management/accounts/edit_user/<string:user>/<int:page>', methods=['GET', 'POST'])
def adminAccountsUserManagement(user, page):
    search_form = AccountManegementForms.tableSearchForm()
    info_forms = AccountManegementForms.adminUserInfoForm()
    name_error = ""
    email_error = ""
    password_error = ""
    active_error = ""
    blacklist_error = ""
    page: int = page
    pages = 3
    URL = f"http://127.0.0.1:5000/admin/management/accounts/edit_user/{user}/"
    user = str(user).replace('%20', ' ')
    user_info = User.query.filter_by(name=user).first()
    article_info = Article.query.filter(Article.author.like(user)).paginate(page, pages, error_out=False)
    if request.method == "POST":
        if info_forms.name.data and info_forms.name.validate(info_forms):
            user_info.name = info_forms.name.data
            user = info_forms.name.data
        elif not info_forms.name.validate(info_forms) and info_forms.name.data:
            name_error = scrapeError(URL, ('id', 'name-err-p'), info_forms.name.errors)
        elif info_forms.email.data and info_forms.email.validate(info_forms):
            user_info.email = info_forms.email.data
        elif not info_forms.email.validate(info_forms) and info_forms.email.data:
            email_error = scrapeError(URL, ('id', 'email-err-p'), info_forms.email.data)
        elif info_forms.password.data and info_forms.password.validate(info_forms):
            user_info.password = sha512_crypt.hash(info_forms.password.data)
        elif not info_forms.password.validate(info_forms) and info_forms.password.data:
            password_error = scrapeError(URL, ('id', 'pwd-err-p'), info_forms.password.errors)
        elif info_forms.active.data and info_forms.active.validate(info_forms):
            if info_forms.active.data == "False":
                data = False
            else:
                data = True
            user_info.active = data
            db.session.commit()
        elif not info_forms.active.validate(info_forms):
            active_error = scrapeError(URL, ('id', 'active-status-err-p'), info_forms.active.errors)
        elif info_forms.blacklist.data and info_forms.blacklist.validate(info_forms):
            if info_forms.blacklist.data == "False":
                data = False
            else:
                data = True
            user_info.blacklisted = data
            db.session.commit()
        elif not info_forms.blacklist.validate(info_forms) and info_forms.blacklist.data:
            blacklist_error = scrapeError(URL, ('id', 'blacklist-status-err-p'), info_forms.blacklist.errors)
        return render_template("private/admin/accountsuser.html", user=user_info, article_info=article_info, search_form=search_form, info_forms=info_forms, name_error=name_error, email_error=email_error, pwd_error=password_error, active_error=active_error, blacklist_error=blacklist_error)
    else:
        return render_template("private/admin/accountsuser.html", user=user_info, article_info=article_info, search_form=search_form, info_forms=info_forms)
        