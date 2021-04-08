# ------------------ Imports ------------------
from ProjectsWebsite import create_app
from ProjectsWebsite.util import initializeSchedulerInspect, checkExpireRegistrationCodes
from flask import render_template, redirect, url_for, send_from_directory
from rich import print as rprint
import os
import schedule

# ------------------ Wsgi App ------------------
app, db = create_app("../.env")

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

# ------------------ Webstarter ------------------
if __name__ == '__main__':
    rprint("[black][PRE-CONNECTING][/black] [bold green]Creating all SQL databases if not exists....[/bold green]") 
    db.create_all(app=app)
    rprint("[bold green] All SQL databases has been created if they haven't been created. [/bold green]")
    rprint("[black][CONNECTING][/black] [bold green]Connecting to website...[/bold green]")
    try:
        cease_schedule_operation = initializeSchedulerInspect()
        app.run()
    except KeyboardInterrupt:
        rprint("[black][Schedule Thread][/black][bold red]Stopping Scheduler operations...[/bold red]")
        cease_schedule_operation.set()
        rprint("[black][Schedule Thread][/black][bold green]Stopping Scheduler operations successfully stopped[/bold green]")
        raise 