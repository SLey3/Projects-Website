# ------------------ Imports ------------------
from flask import (
    Blueprint, redirect,
    url_for, request,
    render_template
)
from flask_security import roles_required, roles_accepted
from flask_admin import Admin, BaseView

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
def dashboard():
    """
    redirects to dashboard home
    """
    return redirect(url_for("dashboard.dashboardHome"))

@dash.route('/home')
@roles_accepted('member', 'admin')
def dashboardHome():
    """
    Dashboard of the website
    """
    return render_template("dashboard.html")


@dash.route('/admin')
@roles_required('admin')
def adminPage():
    """
    Administrator Page
    """
    return redirect(url_for("admin.index"))