# ------------------ Imports ------------------
import sys
sys.path.insert(0, '.')
del sys
from flask import (
    Flask, request, render_template, 
    redirect, url_for, send_from_directory
    )
from flask_login import current_user
from flask_security import Security
from flask_session import Session
from flask_uploads import configure_uploads
from datetime import timedelta
from subprocess import Popen, PIPE, TimeoutExpired
from admin import admin
from dashboard import dash
from forms import loginForm
from database.models import db
import ssl
import os

# ------------------ Check Directories ------------------
if os.path.basename(os.getcwd()) == "Projects_Website":
    directory_script = Popen(["sh", "./scripts/checkdirs.sh"], stdin=PIPE, stdout=PIPE, stderr=PIPE) 
    directory_script.communicate()
else:
    directory_script = Popen(["sh", "../scripts/checkdirs.sh"], stdin=PIPE, stdout=PIPE, stderr=PIPE) 
    directory_script.communicate()


# ------------------ SSL ------------------
context = ssl.SSLContext()
context.load_cert_chain('cert/cert.crt', 'cert/key.pem')

# ------------------ App Setup ------------------
app = Flask(__name__, template_folder="templates", static_folder='static')
app.config["UPLOADS_DEFAULT_DEST"] = f'{app.root_path}\\static\\assets\\uploads'
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=5, hours=12, minutes=6, seconds=59)
app.config["SESSION_FILE_DIR"] = f'{app.root_path}\\static\\sess'
app.config.from_pyfile("../.env")
import views
app.register_blueprint(dash)
app.register_blueprint(admin)
app.register_blueprint(views.main_app)
app.add_template_global(current_user, 'current_user')
app.add_template_global(request, 'request')
app.add_template_global(redirect, 'redirect')

db.init_app(app)

views.login_manager.init_app(app)

views.mail.init_app(app)

configure_uploads(app, views.img_set)

views.assets.init_app(app)

views.alert.init_app(app)

views.security.init_app(app, views.user_datastore, login_form=loginForm)

Session(app)

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
    app.run(debug=True, ssl_context=context)        