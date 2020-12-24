# ------------------ Imports ------------------
from flask import (
    Blueprint, redirect,
    url_for, request,
    render_template,
    abort
)
from flask_security import roles_required, roles_accepted
from flask_login import login_required

# ------------------ Blueprint Config ------------------
dash = Blueprint('dashboard', __name__, static_folder='static', template_folder="templates/private", url_prefix='/dashboard')

# ------------------ Dashboard urls ------------------

@dash.route('/')
@roles_accepted('member', 'admin')
@roles_required('verified')
@login_required
def dashboard():
    """
    redirects to dashboard home
    """
    return redirect(url_for("dashboard.dashboardHome"))

@dash.route('/home')
@dash.route('/home/')
@roles_accepted('member', 'admin')
@roles_required('verified')
@login_required
def dashboardHome():
    """
    Dashboard of the website
    """
    return abort(400)

@dash.route('/create_article')
@dash.route('/create_article/')
@dash.route('/home/create_article/')
@roles_accepted('admin', 'editor')
@roles_required('verified')
@login_required
def create_article_redirect():
    return redirect(url_for("articleCreation"))