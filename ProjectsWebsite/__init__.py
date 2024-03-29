# ------------------ Imports ------------------
import sys

sys.path.insert(0, ".")
del sys
import logging
import os
import ssl
from json import load
from pathlib import Path

try:
    import flask_monitoringdashboard as MonitorDashboard
except ImportError:
    MonitorDashboard = None
import pendulum
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask.logging import create_logger
from flask_debugtoolbar import DebugToolbarExtension
from flask_praetorian import PraetorianError
from flask_uploads import configure_uploads
from rich import print as rprint
from sqlalchemy.orm.session import Session as SQLSession

from ProjectsWebsite.forms import loginForm
from ProjectsWebsite.modules import (
    assets,
    cors,
    db,
    guard,
    img_set,
    login_manager,
    mail,
    migrate,
    security,
    sess,
)
from ProjectsWebsite.util import appExitHandler, current_user
from ProjectsWebsite.util.utilmodule import alert

path = Path(os.path.dirname(os.path.abspath(__file__)))

sql_sess = SQLSession(autoflush=False)

# ------------------ SSL ------------------
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain("cert/server.cert", "cert/server.key")

# ------------------ App Setup ------------------
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["FLASK_SKIP_DOTENV"] = 1
app.config["UPLOADS_DEFAULT_DEST"] = f"{app.static_folder}/assets/uploads"
app.config["PERMANENT_SESSION_LIFETIME"] = pendulum.duration(5, 59, 1, 100, 59, 15)
app.config["SESSION_FILE_DIR"] = f"{app.static_folder}/sess"
app.config["ALERT_CODES_DICT"] = load(
    open(f"{app.static_folder}/assets/json/errors.json")
)
app.config.from_pyfile("../.env")
app.register_error_handler(
    PraetorianError,
    PraetorianError.build_error_handler(lambda e: logging.error(e.message)),
)
app.debug = True

app.env = "development"

app.config["TESTING"] = False

if not app.config["TESTING"]:
    if MonitorDashboard:
        MonitorDashboard.config.init_from(
            file=path.parent / "monitor_config.cfg", log_verbose=True
        )
        MonitorDashboard.bind(app)
    else:
        rprint(
            "[red]MonitorDashboard is unavailable and thus marked as Inop. Check for future versions that support py310[/red]"
        )
        app.add_template_global(MonitorDashboard, "__monitordashboard")

db.init_app(app)

login_manager.init_app(app)

mail.init_app(app)

migrate.init_app(app, db, f"{path}/migrations")

configure_uploads(app, img_set)

assets.init_app(app)

alert.init_app(app)

try:
    from ProjectsWebsite.database.models import User, user_datastore
except ModuleNotFoundError:
    from .database.models import User, user_datastore

security.init_app(app, user_datastore, login_form=loginForm)

guard.init_app(app, User)

cors.init_app(app)

sess.init_app(app)

if app.env == "developement":
    toolbar = DebugToolbarExtension(app)

try:
    from ProjectsWebsite.admin import admin
    from ProjectsWebsite.dashboard import dash
except ModuleNotFoundError:
    from .admin import admin
    from .dashboard import dash

# ------------------ Blueprint registration ------------------
try:
    from ProjectsWebsite.views import main_app
except ModuleNotFoundError:
    from .views import main_app

app.register_blueprint(dash)
app.register_blueprint(admin)
app.register_blueprint(main_app)

# ------------------ template globals ------------------
app.add_template_global(current_user, "current_user")
app.add_template_global(app, "current_app")
app.add_template_global(request, "request")
app.add_template_global(redirect, "redirect")

# ------------------ before first request ------------------
@app.before_first_request
def find_or_create_roles():
    user_datastore.find_or_create_role("admin")
    user_datastore.find_or_create_role("member")
    user_datastore.find_or_create_role("unverified")
    user_datastore.find_or_create_role("verified")
    user_datastore.find_or_create_role("editor")
    create_logger(app)


# ------------------ error handlers ------------------
@app.errorhandler(404)
def page_not_found(e):
    """
    handles 404 status code and 404 error page
    """
    return render_template("public/error_page/404/404.html")


@app.errorhandler(500)
def server_error(e):
    """
    handles 500 status code and redirects to HomePage
    """
    alert.setAlert("error", "2")
    return redirect(url_for("main_app.homePage"))


@app.errorhandler(403)
def inauthorized_perm_error(e):
    """
    handles 403 status code and redirects to HomePage
    """
    alert.setAlert("error", "3")
    return redirect(url_for("main_app.homePage"))


@app.errorhandler(401)
def inauthorized_auth_error(e):
    """
    handles 401 status code and redirects to HomePage
    """
    alert.setAlert("error", "4")
    return redirect(url_for("main_app.homePage"))


@app.errorhandler(422)
def unprocessable_err_handler(e):
    headers = e.data.get("headers", None)
    messages = e.data.get("messages", ["Invalid request."])
    if headers:
        return (
            jsonify({"errors": messages, "code": e.code, "headers": headers}),
            e.code,
            headers,
        )
    else:
        return jsonify({"errors": messages, "Code": e.code}), e.code


# ------------------ favicon ------------------
@app.route("/favicon.ico")
def favicon():
    """
    web logo
    """
    return send_from_directory(
        os.path.join(app.root_path, "static", "assets", "favicon"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


# ------------------ Webstarter ------------------
if __name__ == "__main__":
    db.create_all(app=app)
    rprint(
        "[black][CONNECTING][/black] [bold green]Connecting to website...[/bold green]"
    )
    with appExitHandler():
        app.run(ssl_context=context)
