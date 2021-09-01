# ------------------ Imports ------------------
from flask import Blueprint, redirect, url_for, request, render_template, abort
from ProjectsWebsite.util import roles_accepted, roles_required, token_auth_required

# ------------------ Blueprint Config ------------------
dash = Blueprint(
    "dboard",
    __name__,
    static_folder="static",
    template_folder="templates/private",
    url_prefix="/dashboard",
)

# ------------------ Dashboard urls ------------------


@dash.route("/")
@roles_accepted("member", "admin")
@token_auth_required
def dashboard():
    """
    redirects to dashboard home
    """
    return redirect(url_for("dashboard.dashboardHome"))


@dash.route("/home")
@dash.route("/home/")
@roles_accepted("member", "admin")
@token_auth_required
def dashboardHome():
    """
    Dashboard of the website
    """
    return "<h1 id='development-warning'>Page is under development</h1>"


@dash.route("/create_article")
@dash.route("/create_article/")
@dash.route("/home/create_article/")
@roles_accepted("admin", "editor")
@token_auth_required
def create_article_redirect():
    return redirect(url_for("articleCreation"))
