# ------------------ Imports ------------------
from flask import (
    Blueprint, redirect,
    url_for, request,
    render_template
)

# ------------------ Blueprint Config ------------------
dash = Blueprint('dashboard', __name__, template_folder="templates/private", url_prefix='/dashboard')

# ------------------ Dashboard urls ------------------

@dash.route('/')
def dashboard():
    """
    redirects to dashboard home
    """
    return redirect(url_for("dashboard.dashboardHome"))

@dash.route('/home')
def dashboardHome():
    """
    Dashboard of the website
    """
    return render_template("dashboard.html")
