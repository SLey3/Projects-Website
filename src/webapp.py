# ------------------ Imports ------------------
import sys
sys.path.insert(0, '.')
del sys
from flask import (
    Flask, render_template,
    redirect, request,
    url_for, abort
)
from src.forms import (
    loginForm, registerForm,
    articleForm, contactForm,
    forgotForm, forgotRequestForm
)
from src.database.models import (
    db, Article, User, Role, Person
)
try:
    from flask_sqlalchemy.orm.session import Session
except ModuleNotFoundError:
    from sqlalchemy.orm.session import Session
from sqlalchemy.exc import OperationalError
from passlib.hash import sha512_crypt
from datetime import timedelta, datetime
from flask_login import (
    LoginManager, login_user, 
    logout_user, current_user
)
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_security import (
    Security, SQLAlchemyUserDatastore, 
    roles_accepted, roles_required, 
    login_required
)
from src.dashboard import dash
from werkzeug.utils import secure_filename
from flask_uploads import UploadSet, IMAGES, configure_uploads
from io import open as iopen
from src.util import (
    AlertUtil, is_valid_article_page, formatPhoneNumber
)
from src.util.helpers import EMAILS
from flask_assets import Bundle, Environment
from src.admin import admin
import base64
import os

# ------------------ path Config ------------------
current_path = os.getcwd()
if 'src' in current_path:
    PATH = current_path
else:
    PATH = os.path.join(current_path, 'src')
    
del current_path
del os

# ------------------ app Config ------------------
app = Flask(__name__, template_folder="templates/public", static_folder='static')
app.config["SECRET_KEY"] = "Kwl986"
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024
app.config["ALERT_CODES_NUMBER_LIST"] = [0, 1, 2]
app.config["ALERT_CODES_DICT"] = {
    0: "Confirmation link expired. You must Register again.",
    1: "Reset Link Expired.",
    2: "Internal Server error. If this happens again contact the administrator."
}
app.config["ALERT_TYPES"] = [
    'info',
    'success',
    'warning',
    'error'
]
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database/users.sqlite3"
app.config["SQLALCHEMY_BINDS"] = {'articles': 'sqlite:///database/articles.sqlite3'}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["RECAPTCHA_PUBLIC_KEY"] = "6LfrfNgZAAAAAKzTPtlo2zh9BYXVNfoVzEHeraZM"
app.config["RECAPTCHA_PRIVATE_KEY"] = "6LfrfNgZAAAAAIFW8pX7L349lOaNam3ARg4nm1yP"
app.config["MAIL_DEFAULT_SENDER"] = "noreplymyprojectsweb@gmail.com"
app.config["MAIL_USERNAME"] = "noreplymyprojectsweb@gmail.com"
app.config["MAIL_PASSWORD"] = "hFb5b4UcwovqTshinAv6exVHY2pUT4N5lY77XRVEfmPFaY98nA9NOsQULJY2IVR66YFIMH6dgtdx9o1VoLLBW4YYrjcjRC10a3v"
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USE_TLS "] = False
app.config["UPLOADS_DEFAULT_DEST"] = f'{PATH}\\static\\assets\\uploads'
app.config["SECURITY_PASSWORD_HASH"] = "sha512_crypt"
app.config["SECURITY_FLASH_MESSAGES"] = False
app.config["SECURITY_LOGIN_URL"] = "/auth/login" or "/auth/login/"
app.config["SECURITY_LOGOUT_URL"] = "/auth/signout" or "/auth/signout/"
app.config["SECURITY_LOGIN_USER_TEMPLATE"] = 'error_page/login_redirect/redirectlogin.html'
app.permanent_session_lifetime = timedelta(days=5)
app.register_blueprint(dash)
app.register_blueprint(admin)
app.add_template_global(current_user, 'current_user')


# ------------------ app Config: SQLAlchemy Config ------------------
db.init_app(app)

sql_sess = Session(autoflush=False)

# ------------------ app Config: Flask_login Config ------------------
login_manager = LoginManager(app)

# ------------------ app Config: Flask_mail Config ------------------
mail = Mail(app)

urlSerializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

# ------------------ app Config: Flask Uploads(Reuploaded) Config ------------------
img_set = UploadSet('images', IMAGES)
configure_uploads(app, img_set)
   
# ------------------ app Config: Bundle Config ------------------ 
assets = Environment(app)

# ------------------ app Config: Bundle Config: Bundles ------------------ 

js_bundle = Bundle('js/src/confirm.js', 'js/src/pass.js', 'js/src/novalidate.js',
                   filters='jsmin', output="js/dist/main.min.js") 

alert_css_bundle = Bundle('styles/alert_css/src/box.css', 'styles/alert_css/src/error.css', 
                    'styles/alert_css/src/info.css', 'styles/alert_css/src/success.css',
                    'styles/alert_css/src/warning.css', filters='cssmin', 
                    output='styles/alert_css/dist/alerts.min.css')

admin_home_css_bundle = Bundle('styles/admin/index/src/index.css', 'styles/admin/util/scrollbar/scrollbar.css',
                               'styles/admin/util/navbar/navbar.css', 'styles/admin/util/management/management.css', 
                               filters='cssmin', output='styles/admin/index/dist/index.min.css')

admin_article_css_bundle = Bundle('styles/admin/accounts/src/index.css', 'styles/admin/util/scrollbar/scrollbar.css',
                                  'styles/admin/util/navbar/navbar.css', 'styles/admin/util/management/management.css',
                                  filters='cssmin', output='styles/admin/accounts/dist/index.min.css')

# ------------------ app Config: Bundle Config: Registration ------------------ 
assets.register('main__js', js_bundle)
  
assets.register('alert__css', alert_css_bundle)

assets.register('admin_dashboard_css', admin_home_css_bundle)

assets.register('admin_articles_css', admin_article_css_bundle)

# ------------------ app Config: AlertUtil Config ------------------
alert = AlertUtil(app)

# ------------------ app Config: Security Loader ------------------
    
user_datastore = SQLAlchemyUserDatastore(db, User, Role)

security = Security(app, user_datastore, login_form=loginForm)

# ------------------ error handlers ------------------
@app.errorhandler(400)
def no_articles(e):
    """
    returns 400 status code and 400 error page
    """
    return render_template('error_page/400/400.html')

@app.errorhandler(404)
def page_not_found(e):
    """
    returns 404 status code and 404 error page
    """
    return render_template('error_page/404/404.html')

@app.errorhandler(500)
def servererror(e):
    """
    returns 500 status code and redirects to HomePage
    """
    alert.setAlert('error', 2)
    return redirect(url_for('homePage'))

# ------------------ LoginManaer: User Resource ------------------
@login_manager.user_loader
def load_user(user_id):
    """
    Gets the User
    """
    return User.query.get(int(user_id))

# ------------------ web pages ------------------

@app.route('/login', methods=["GET", "POST"])
@app.route('/login/', methods=["GET", "POST"])
def loginPage():
    """
    main front page
    """
    form = loginForm()
    
    alert_dict = alert.getAlert()
    
    if request.method == "POST" and form.validate_on_submit():
        user = User.query.filter_by(email=form.username.data.lower()).first()
        if user:
            if sha512_crypt.verify(form.password.data, user.password):
                login_user(user)
                return redirect(url_for("homePage"))
        error = "Invalid Email or Password"
        return render_template("loginpage.html", form=form, error=error, alert_msg=alert_dict['Msg'], alert_type=alert_dict['Type'])
    else:
        if current_user.is_authenticated:
            return redirect(url_for("homePage"))
        else:
            return render_template("loginpage.html", form=form, alert_msg=alert_dict['Msg'], alert_type=alert_dict['Type'])

@app.route('/register', methods=['GET', 'POST'])
@app.route('/register/', methods=['GET', 'POST'])
def registerPage():
    """
    Registration Page
    """
    form = registerForm()
    if request.method == "POST" and form.validate_on_submit():
        with sql_sess.no_autoflush:
            user_datastore.find_or_create_role('admin')
            user_datastore.find_or_create_role('member')
            user_datastore.find_or_create_role('unverified')
            user_datastore.find_or_create_role('verified')
        user_datastore.create_user(
            name=form.name.data,
            email=form.email.data.lower(),
            password=sha512_crypt.hash(form.password.data),
            roles=['member', 'unverified']
        )
        db.session.commit()
        EMAILS.append(form.email.data)
        token = urlSerializer.dumps(form.email.data, salt='email-confirm')
        verify_msg = Message('Confirm Account', recipients=[form.email.data])
        confirm_link = 'http://127.0.0.1:5000' + url_for("confirmation_recieved", token=token, external=True)
        verify_msg.body = f'''Thank you for registering, {form.name.data}! In order to complete the registration you must click on the link below.
        Link will expire in 30 minutes after this email has been sent.
        Link: {confirm_link}'''
        mail.send(verify_msg)
        alert.setAlert('success', 'Registration Succesful. Check your email for confirmation link.')
        return redirect(url_for("loginPage"))
    else:
        return render_template("registerpage.html", form=form)
    
@app.route('/confirm_recieved/<token>')  
@app.route('/confirm_recieved/<token>/')  
def confirmation_recieved(token):
    """
    Confirmation and account creation page
    :param token: Email token
    """
    try:
        urlSerializer.loads(token, salt="email-confirm", max_age=3600/2)
        email = EMAILS.pop(0)
        user_datastore.remove_role_from_user(user_datastore.get_user(email), 'unverified')
        user_datastore.add_role_to_user(user_datastore.get_user(email), "verified")
        db.session.commit()
        alert.setAlert('success', 'Email Verified')
        return redirect(url_for("loginPage"))
    except SignatureExpired:
        email_string = EMAILS.pop(0)
        User.query.filter_by(email=email_string).delete()
        db.session.commit()
        alert.setAlert('error', 0)
        return redirect(url_for("loginPage"))
    
@app.route('/login/forgotpwd', methods=['GET', 'POST'])
@app.route('/login/forgotpwd/', methods=['GET', 'POST'])
def initialForgotPage():
    """
    forgot password page.
    """
    form = forgotRequestForm()
    if request.method == "POST":
        recipient_email = form.email.data
        user = User.query.filter_by(email=recipient_email.lower()).first()
        if isinstance(user, type(None)):
            if recipient_email != '' and form.submit.data == True:
                form.back_button.raw_data.insert(0, '.')
            if recipient_email == '':
                return redirect(url_for('loginPage'))
            elif form.back_button.raw_data.pop(0) == '':
                return redirect(url_for('loginPage'))
            else:
                alert.setAlert('warning', f"No Account found under {recipient_email}.")
                return redirect(url_for("loginPage"))
        
        if not form.submit.data:
            return redirect(url_for('loginPage')) 
        reset_token = urlSerializer.dumps(recipient_email, salt="forgot-pass")
        reset_url = 'http://127.0.0.1:5000' + url_for("resetRequestRecieved", token=reset_token, email=recipient_email)
        reset_msg = Message('Reset Password', recipients=[recipient_email])
        reset_msg.body = f"""
        Dear User,
        You have requested to reset your password. Follow the link below to reset your password.
        Reset Password: {reset_url}
        """
        mail.send(reset_msg)
        alert.setAlert('success', 'Reset Password Email has been sent.')
        return redirect(url_for('loginPage'))
    else:
        return render_template("forgot.html", field=form)
    
@app.route('/login/forgotpwd/<token>/<email>', methods=['GET', 'POST'])
@app.route('/login/forgotpwd/<token>/<email>/', methods=['GET', 'POST']) 
def resetRequestRecieved(token, email):
    """
    Redirects to Reset Form link after validating token
    """
    try:
        urlSerializer.loads(token, salt="forgot-pass", max_age=300)
        
        form = forgotForm()
        if request.method == 'POST':
            email = str(email).replace("%40", '@')
            replacementPassword = sha512_crypt.hash(form.confirm_new_password.data)
            user = User.query.filter_by(email=email).first()
            if not sha512_crypt.verify(form.confirm_new_password.data, user.password):
                user.password = replacementPassword
                db.session.commit()
                alert.setAlert('success', 'Password has been Successfully reset.')
            else:
                alert.setAlert('warning', 'The Requested Password matches your current password.')
            return redirect(url_for('loginPage'))
        else:
            return render_template("forgotrecieved.html", form=form, token=token, email=email)
    
    except SignatureExpired:
        alert.setAlert('error', 1)
        return redirect(url_for("loginPage"))
    
@app.route('/signout')
@app.route('/signout/')
@login_required
def signOut():
    """
    Signs out of the site
    """
    logout_user()
    form = loginForm()
    alert.setAlert('success', 'Succesfully signed out')
    return redirect(url_for("homePage"))
    
@app.route('/')
@app.route('/')
def homePage():
    """
    website homepage
    """
    alert_dict = alert.getAlert()
    return render_template("homepage.html", alert_msg=alert_dict['Msg'], alert_type=alert_dict['Type'])

@app.route('/home')
@app.route('/home/')
def redirectToHomePage():
    """
    redirects to homepage
    """
    return redirect(url_for('homePage'))
    
@app.route('/about')
@app.route('/about/')
def aboutPage():
    return render_template('aboutpage.html')

@app.route('/articles/create_article', methods=['GET', 'POST'])
@app.route('/articles/create_article/', methods=['GET', 'POST'])
@login_required
@roles_accepted('admin', 'editor')
def articleCreation():
    form = articleForm()
    if request.method == "POST" and form.validate_on_submit():
        img_file = form.front_image.data
        if isinstance(img_file, type(None)):
            del img_file
            img = "None"
        else:
            filename = secure_filename(img_file.filename)
            img_set.save(img_file, name=f"{filename}")
            with iopen(f'{PATH}\\static\\assets\\uploads\\images\\{filename}', 'rb') as image:
                img = str(base64.b64encode(image.read()), 'utf-8')
        current_date = datetime.now()
        creation_date = f"{current_date.month}/{current_date.day}/{current_date.year}"
        del current_date
        body = request.form.get('editordata')          
        new_article = Article(
            title=form.title.data,
            author=form.author.data,
            create_date=creation_date,
            short_desc=form.short_desc.data,
            title_img=img,
            body=body
        )
        db.session.add(new_article)
        db.session.commit()
        alert.setAlert('success', 'Article has been Created.')
        return redirect(url_for("homePage"))
    else:
        return render_template("articles/articleform.html", form=form)
    
@app.route('/articles', methods=['GET', 'POST'])
@app.route('/articles/', methods=['GET', 'POST'])
def article_home():
    try:
        articles = Article.query.all()
    except OperationalError:
        abort(400)
    return render_template("articles/articlepage.html", articles=articles)

@app.route('/articles/<string:id>')
@app.route('/articles/<string:id>/')
@is_valid_article_page
def articlePage(id):
    try:
        article = Article.query.filter_by(id=id).first()
    except OperationalError:
        abort(404)
    return render_template('articles/articleviewpage.html', article=article)

@app.route('/contact', methods=['GET', 'POST'])
@app.route('/contact/', methods=['GET', 'POST'])
def contact_us():
    form = contactForm()
    if request.method == 'POST' and form.validate_on_submit():
        name = form.first_name.data + " " + form.last_name.data
        inquiry_selection = dict(form.inquiry_selection.choices).get(form.inquiry_selection.data)
        email = form.email.data
        tel = formatPhoneNumber(form.mobile.data)
        msg = form.message.data
        mail_msg = Message(f'Contact Message Recieved', recipients=["ghub4127@gmail.com", "noreplymyprojectsweb@gmail.com"])
        mail_msg.body = f"""
        Contact:
        Name: {name}
        Inquiry Selection: {inquiry_selection}
        Email: {email}
        Telephone Number: {tel}
        -------------------------------------------------------------
        Message:
        {msg}
        """
        mail.send(mail_msg)
        alert.setAlert('info', 'Contact Message has been Sent. Please wait for a responce from support team.')
        return redirect(url_for('homePage'))
    else:
        return render_template('contactpage.html', form=form)

@app.route('/home/admin')
@app.route('/home/admin/')   
@roles_required('admin', 'verified')
@login_required
def adminPage():
    """
    Administrator Page
    """
    return redirect(url_for("admin.adminHomePage"))

# ------------------ Website Starter ------------------
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
    app.run(debug=True)