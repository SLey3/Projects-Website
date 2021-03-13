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
from ProjectsWebsite.util import current_user
from http.client import HTTPConnection as reqlogConnection
import ssl
import os
import logging

# ------------------ Check Directories ------------------
if os.path.basename(os.getcwd()) == "Projects_Website":
    directory_script = Popen(["sh", "./scripts/checkdirs.sh"], stdin=PIPE, stdout=PIPE, stderr=PIPE) 
    directory_script.communicate()
else:
    directory_script = Popen(["sh", "../scripts/checkdirs.sh"], stdin=PIPE, stdout=PIPE, stderr=PIPE) 
    directory_script.communicate()


# ------------------ Production Status ------------------
# set true if website is in production, else set false if website is in development
PRODUCTION = False



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
app.config["UPLOADS_DEFAULT_DEST"] = f'{app.root_path}\\static\\assets\\uploads'
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=5)
app.config["SESSION_FILE_DIR"] = f'{app.root_path}\\static\\sess'
app.config.from_pyfile("../.env")
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

# ------------------ error handlers ------------------
@app.errorhandler(400)
def no_articles(e):
    """
    returns 400 status code and 400 error page
    """
    return render_template('public/error_page/400/400.html'), 400

@app.errorhandler(404)
def page_not_found(e):
    """
    returns 404 status code and 404 error page
    """
    return render_template('public/error_page/404/404.html'), 404

@app.errorhandler(500)
def servererror(e):
    """
    returns 500 status code and redirects to HomePage
    """
    src.views.alert.setAlert('error', 2)
    return redirect(url_for('main_app.homePage')), 500


# ------------------ favicon ------------------
@app.route('/favicon.ico')
def favicon():
    """
    web logo
    """
    return send_from_directory(os.path.join(app.root_path, 'static', 'assets', 'favicon'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# ------------------ Webstarter ------------------
if __name__ == '__main__':
    from rich.console import Console
    from rich.progress import Progress
    from time import sleep
    
    console = Console()
    
    console.print("[black][PRE-CONNECTING][/black] [bold green]Creating all SQL databases if not exists....[/bold green]")
    with Progress() as progress:
        sql_database_task = progress.add_task("[cyan] Creating SQL Databases...", total=85)
        
        db.create_all(app=app)
        while not progress.finished:
            progress.update(sql_database_task, advance=1.5)
            sleep(0.02)
    console.log("[bold green] All SQL databases has been created if they haven't been created. [/bold green]")
    console.print("[black][CONNECTING][/black] [bold green]Connecting to website...[/bold green]")
    sleep(1)
    app.run()        