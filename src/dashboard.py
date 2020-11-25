# ------------------ Imports ------------------
from flask import (
    Blueprint, redirect,
    url_for, request,
    render_template
)
from flask_security import roles_required, roles_accepted
from flask_admin import Admin, BaseView
from flask_login import login_required

# ------------------ Blueprint Config ------------------
dash = Blueprint('dashboard', __name__, template_folder="templates/private", url_prefix='/dashboard')

# ------------------ Admin MyView class ------------------
    
class MyView(BaseView):
    def __init__(self, *args, **kwargs):
        self._default_view = True
        super(MyView, self).__init__(*args, **kwargs)
        self.admin = Admin()    

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
    return render_template("dashboard.html")


@dash.route('/admin')
@dash.route('/admin/')
@roles_required('admin', 'verified')
@login_required
def adminPage():
    """
    Administrator Page
    """
    return redirect(url_for("admin.index"))

@dash.route('/create_article')
@dash.route('/create_article/')
@dash.route('/home/create_article/')
@roles_accepted('admin', 'editor')
@roles_required('verified')
@login_required
def create_article_redirect():
    return redirect(url_for("articleCreation"))