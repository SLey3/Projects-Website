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
from src.util.helpers import bool_re, email_re
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
        elif not info_forms.name.validate(info_forms):
            with requests.Session() as sess:
                web = sess.get(URL)
                soup = BeautifulSoup(web.content, 'html5lib')
                p_name_tag = soup.find_all('p', {'id':'name-err-p'})
                for p_tag in p_name_tag:                   
                    for error in info_forms.name.errors:
                        p_tag.insert(0, NavigableString(f"- {error}\n"))
                        name_error = p_tag
        elif info_forms.email.data and info_forms.email.validate(info_forms):
            user_info.email = info_forms.email.data
        elif not info_forms.email.validate(info_forms):
            with requests.Session() as sess:
                web = sess.get(URL)
                soup = BeautifulSoup(web.content, 'html5lib')
                p_email_tag = soup.find_all('p', {'id':'email-err-p'})
                for p_tag in p_email_tag:
                    for error in info_forms.email.errors:
                        p_tag.insert(0, NavigableString(f"- {error}\n"))
                        email_error = p_tag
        elif info_forms.password.data and info_forms.password.validate(info_forms):
            user_info.password = sha512_crypt.hash(info_forms.password.data)
        elif not info_forms.password.validate(info_forms):
            with requests.Session() as sess:
                web = sess.get(URL)
                soup = BeautifulSoup(web.content, 'html5lib')
                p_pwd_tag = soup.find_all('p', {'id':'pwd-err-p'})
                for p_tag in p_email_tag:
                    for error in info_forms.password.errors:
                        p_tag.insert(0, NavigableString(f"- {error}\n"))
                        password_error = p_tag
        elif info_forms.active.data and info_forms.active.validate(info_forms):
            user_info.active = info_forms.active.data
        elif not info_forms.active.validate(info_forms):
            with requests.Session() as sess:
                web = sess.get(URL)
                soup = BeautifulSoup(web.content, 'html5lib')
                p_active_tag = soup.find_all('p', {'id':'active-status-err-p'})
                for p_tag in p_active_tag:
                    for error in info_forms.active.errors:
                        p_tag.insert(0, NavigableString(f"- {error}\n"))
                        active_error = p_tag
        elif info_forms.blacklist.data and info_forms.blacklist.validate(info_forms):
            user_info.blacklisted = info_forms.blacklist.data
        elif not info_forms.blacklist.validate(info_forms):
            with requests.Session() as sess:
                web = sess.get(URL)
                soup = BeautifulSoup(web.content, 'html5lib')
                p_blacklist_tag = soup.find_all('p', {'id':'blacklist-status-err-p'})
                for p_tag in p_blacklist_tag:
                    for error in info_forms.blacklist.errors:
                        p_tag.insert(0, NavigableString(f"- {error}\n"))
                        blacklist_error = p_tag
        db.session.commit()
        return render_template("private/admin/accountsuser.html", user=user_info, article_info=article_info, search_form=search_form, info_forms=info_forms, name_error=name_error, email_error=email_error, pwd_error=password_error, active_error=active_error, blacklist_error=blacklist_error)
    else:
        return render_template("private/admin/accountsuser.html", user=user_info, article_info=article_info, search_form=search_form, info_forms=info_forms)
        