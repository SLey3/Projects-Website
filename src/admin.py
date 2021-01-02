# ------------------ Imports ------------------
from flask import (
    Blueprint, render_template, url_for,
    redirect
)
from flask_login import login_required, confirm_login
from flask_security import roles_required

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

@admin.route('/manegement/accounts', methods=['GET', 'POST'])
@admin.route('/manegement/accounts/', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'verified')
def adminAccountsManegement():
    """
    Administrator Account Manegement page
    """
    return render_template("admin/accounts.html")