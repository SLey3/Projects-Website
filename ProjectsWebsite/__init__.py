# ------------------ Imports ------------------
import sys
sys.path.insert(0, '.')
del sys
from flask import (
    Flask, request, render_template, 
    redirect, url_for, send_from_directory
    )
from flask_security import Security
from flask_praetorian import PraetorianError
from flask_session import Session
from flask_uploads import configure_uploads
from flask_debugtoolbar import DebugToolbarExtension
from datetime import timedelta
from subprocess import Popen, PIPE, TimeoutExpired
from ProjectsWebsite.admin import admin
from ProjectsWebsite.dashboard import dash
from ProjectsWebsite.forms import loginForm
from ProjectsWebsite.database.models import User, user_datastore
from ProjectsWebsite.modules import (
    assets, db, guard, login_manager,
    mail, security, img_set
)
from ProjectsWebsite.util.utilmodule import alert
from ProjectsWebsite.util import current_user, runSchedulerInspect, checkExpireRegistrationCodes
from http.client import HTTPConnection as reqlogConnection
from threading import Event
from json import load
from rich import print as rprint
import ssl
import os
import logging
import schedule
import signal

# ------------------ Check Directories ------------------
if os.path.basename(os.getcwd()) == "Projects_Website":
    directory_script = Popen(["sh", "./scripts/checkdirs.sh"], stdin=PIPE, stdout=PIPE, stderr=PIPE) 
    directory_script.communicate()
else:
    directory_script = Popen(["sh", "../scripts/checkdirs.sh"], stdin=PIPE, stdout=PIPE, stderr=PIPE) 
    directory_script.communicate()


# ------------------ Production Status ------------------
# set true if website is in production, else set false if website is in development
PRODUCTION = True



# ------------------ Loggers ------------------
requests_logger = logging.getLogger("urllib3")
requests_logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
requests_logger.addHandler(ch)
reqlogConnection.debuglevel = 1


# ------------------ SSL ------------------
context = ssl.SSLContext()
context.load_cert_chain('cert/server.cert', 'cert/server.key')

# ------------------ App Setup ------------------
app = Flask(__name__, template_folder="templates", static_folder='static')
app.config["FLASK_SKIP_DOTENV"] = 1
app.config["UPLOADS_DEFAULT_DEST"] = f'{app.root_path}\\static\\assets\\uploads'
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=5)
app.config["SESSION_FILE_DIR"] = f'{app.root_path}\\static\\sess'
app.config["ALERT_CODES_DICT"] = load(open(os.path.join(app.root_path, "static", "assets", "json", "errors.json")))
app.config.from_pyfile("../.env")
import ProjectsWebsite.views as views
app.register_blueprint(dash)
app.register_blueprint(admin)
app.register_blueprint(views.main_app)
app.add_template_global(current_user, 'current_user')
app.add_template_global(request, 'request')
app.add_template_global(redirect, 'redirect')
app.register_error_handler(PraetorianError, 
                           PraetorianError.build_error_handler(lambda e: logging.error(e.message)))
app.debug = True

app.env = "development"

db.init_app(app)

login_manager.init_app(app)

mail.init_app(app)

configure_uploads(app, img_set)

assets.init_app(app)

alert.init_app(app)

security.init_app(app, user_datastore, login_form=loginForm)

guard.init_app(app, User)

Session(app)

if not PRODUCTION:
    toolbar = DebugToolbarExtension(app)
    
def create_app(env_dir=None):
    app = Flask(__name__, template_folder="templates", static_folder='static')
    app.config["FLASK_SKIP_DOTENV"] = 1
    app.config["UPLOADS_DEFAULT_DEST"] = f'{app.root_path}\\static\\assets\\uploads'
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=5)
    app.config["SESSION_FILE_DIR"] = f'{app.root_path}\\static\\sess'
    app.config["ALERT_CODES_DICT"] = load(open(os.path.join(app.root_path, "static", "assets", "json", "errors.json")))
    app.config.from_pyfile(env_dir)
    import ProjectsWebsite.views as views
    app.register_blueprint(dash)
    app.register_blueprint(admin)
    app.register_blueprint(views.main_app)
    app.add_template_global(current_user, 'current_user')
    app.add_template_global(request, 'request')
    app.add_template_global(redirect, 'redirect')
    app.register_error_handler(PraetorianError, 
                            PraetorianError.build_error_handler(lambda e: logger.error(e.message)))
    app.debug = True
    
    app.env = "development"

    db.init_app(app)

    login_manager.init_app(app)

    mail.init_app(app)

    configure_uploads(app, img_set)

    assets.init_app(app)

    alert.init_app(app)

    security.init_app(app, user_datastore, login_form=loginForm)

    guard.init_app(app, User)

    Session(app)

    if not PRODUCTION:
        toolbar = DebugToolbarExtension(app)
    requests_logger = logging.getLogger("urllib3")
    requests_logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    requests_logger.addHandler(ch)
    reqlogConnection.debuglevel = 1
    return app

# ------------------ error handlers ------------------
@app.errorhandler(404)
def page_not_found(e):
    """
    handles 404 status code and 404 error page
    """
    return render_template('public/error_page/404/404.html')

@app.errorhandler(500)
def server_error(e):
    """
    handles 500 status code and redirects to HomePage
    """
    alert.setAlert('error', "2")
    return redirect(url_for('main_app.homePage'))

@app.errorhandler(403)
def inauthorized_perm_error(e):
    """
    handles 403 status code and redirects to HomePage
    """
    alert.setAlert('error', "3")
    return redirect(url_for('main_app.homePage'))

@app.errorhandler(401)
def inauthorized_auth_error(e):
    """
    handles 401 status code and redirects to HomePage
    """
    alert.setAlert('error', "4")
    return redirect(url_for('main_app.homePage'))

# ------------------ favicon ------------------
@app.route('/favicon.ico')
def favicon():
    """
    web logo
    """
    return send_from_directory(os.path.join(app.root_path, 'static', 'assets', 'favicon'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    
# ------------------ Exit handler ------------------
class appExitHandler(object):
    def __enter__(self):
        schedule.every(1).hour.do(checkExpireRegistrationCodes)
        self.thread_event = runSchedulerInspect()
        def _signal_handler(signal, frame):
            from sys import exit
            rprint("[black]Schedule[/black][red]Stopping schedule operation[/red]")
            self.thread_event.set()
            rprint("[black]Schedule[/black][bold green]Schedule Operation stopped successfully...[/bold green]")
            return exit(0)
        signal.signal(signal.SIGINT, _signal_handler)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        return exc_type is None
    
# ------------------ Webstarter ------------------
if __name__ == '__main__':
    schedule.every(1).hour.do(checkExpireRegistrationCodes)
    rprint("[black][PRE-CONNECTING][/black] [bold green]Creating all SQL databases if not exists....[/bold green]") 
    db.create_all(app=app)
    rprint("[bold green] All SQL databases has been created if they haven't been created. [/bold green]")
    rprint("[black][CONNECTING][/black] [bold green]Connecting to website...[/bold green]")
    with appExitHandler():
        app.run()