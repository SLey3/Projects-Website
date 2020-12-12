# ------------------ Imports ------------------
from flask import (
    Flask, render_template,
    redirect, request,
    url_for, abort
)
from forms import (
    loginForm, registerForm,
    articleForm, contactForm,
    forgotForm
)
from forms.field import EmailField
from flask_sqlalchemy import SQLAlchemy
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
from flask_admin import Admin, expose, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_security import (
    Security, SQLAlchemyUserDatastore,
    UserMixin, RoleMixin, roles_accepted,
    roles_required, login_required
)
from dashboard import dash
from werkzeug.utils import secure_filename
from flask_uploads import UploadSet, IMAGES, configure_uploads
from io import open as iopen
from functools import wraps
from flask_assets import Bundle, Environment
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


# ------------------ app Config: SQLAlchemy Config ------------------
db = SQLAlchemy(app)

sql_sess = Session(autoflush=False)

# ------------------ app Config: Flask_login Config ------------------
login_manager = LoginManager()
login_manager.init_app(app)

# ------------------ app Config: Flask_mail Config ------------------
mail = Mail()
mail.init_app(app)

urlSerializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

# ------------------ app Config: Admin Config ------------------
admin = Admin(app, template_mode="bootstrap4")

# ------------------ app Config: Flask Uploads(Reuploaded) Config ------------------
img_set = UploadSet('images', IMAGES)
configure_uploads(app, img_set)
   
# ------------------ app Config: Bundle Config ------------------ 
assets = Environment(app)

# ------------------ app Config: Bundle Config: Bundles ------------------ 

js_bundle = Bundle('js/src/confirm.js', 'js/src/pass.js', 'js/src/novalidate.js',
                   filters='jsmin', output="js/dist/main.min.js") 

# ------------------ app Config: Bundle Config: Registration ------------------ 
assets.register('main__js', js_bundle)
  
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
      
# ------------------ SQL classes ------------------
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    person_id = db.Column(db.Integer(), db.ForeignKey("person.id"))
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    
    def __repr__(self):
        return f"Permission: {self.name}"
    
    
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    account = db.relationship("User", primaryjoin="and_(Person.id==User.person_id)")
    role = db.relationship("Role", backref='roles', primaryjoin="and_(Person.id==Role.person_id)")
    
    def __repr__(self):
        return f"Person({name})"
    
class User(db.Model, UserMixin):
    """
    User Model
    """
    id = db.Column("id", db.Integer, primary_key=True)
    person_id = db.Column(db.Integer(), db.ForeignKey("person.id"))
    name = db.Column("name", db.String(100))
    email = db.Column("email", db.String(100), unique=True)
    password = db.Column("password", db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
        
    def __repr__(self):
        return f"Name: {self.name}"
     
class Article(db.Model):
    """
    Article Model
    """
    __bind_key__ = 'articles'
    id = db.Column("id", db.Integer, primary_key=True)
    title = db.Column("title", db.String(100))
    author = db.Column("author", db.String(100))
    create_date = db.Column(db.String(100))
    short_desc = db.Column("short_description", db.String(150))
    title_img = db.Column(db.String(500))
    body = db.Column("body", db.String(900))
    
user_datastore = SQLAlchemyUserDatastore(db, User, Role)

security = Security(app, user_datastore, login_form=loginForm)

# ------------------ Admin pages ------------------
class BacktoDashboard(BaseView):
    @expose('/')
    def index(self):
        """
        Returns to the dashboard
        """
        return redirect(url_for("dashboard.dashboardHome"))
    
admin.add_view(BacktoDashboard(name="back", endpoint="redirect"))
admin.add_view(ModelView(Person, db.session))

# ------------------ External Resources ------------------
@login_manager.user_loader
def load_user(user_id):
    """
    Gets the User
    """
    return User.query.get(int(user_id))



def get_alert_type():
    """
    Gets alert type
    
    Returns:
        ALERTS[Type]
    """
    if alert_method['method'] != '':
        Type = alert_method['method']
        alert_method.update(method='')
        check_list = list(ALERTS.items())
        if Type not in check_list:
            return Type
        else:
            return ALERTS[Type]
    return ""


def is_valid_article_page(func):
    """
    Returns whether the article page is valid or not.
    if not valid:
    Returns:
        404 http code
    """
    @wraps(func)
    def validator(id):
        articles = Article.query.all()
        for article in articles:
            article_id_number = str(article.id)
            if id == article_id_number:
                return func(id)
        return abort(404)
    return validator

# ------------------ External Resources: Constants and variables ------------------

EMAILS = []

ALERTS = {
    'success' : 'alert-success',
    'error' : 'alert-danger',
    'warn': 'alert-warnings'
}

alert_method = {'method': ''}

# ------------------ web pages ------------------

@app.route('/', methods=["GET", "POST"])
def loginPage():
    """
    main front page
    """
    form = loginForm()
    
    alert_type = get_alert_type()
    
    if request.method == "POST" and form.validate_on_submit():
        user = User.query.filter_by(email=form.username.data).first()
        if user:
            if sha512_crypt.verify(form.password.data, user.password):
                login_user(user)
                return redirect(url_for("homePage"))
        error = "Invalid Email or Password"
        return render_template("loginpage.html", form=form, error=error, alert_type=alert_type)
    else:
        if current_user.is_authenticated:
            return redirect(url_for("homePage"))
        else:
            return render_template("loginpage.html", form=form, alert_type=alert_type)

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
            email=form.email.data,
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
        alert_method.update(method='Registration Succesful. Verification required, check your email for confirmation link.')
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
        alert_method.update(method='Email Verified')
        return redirect(url_for("loginPage"))
    except SignatureExpired:
        email_string = EMAILS.pop(0)
        User.query.filter_by(email=email_string).delete()
        db.session.commit()
        alert_method.update(method='Confirmation link expired. You must Register again')
        return redirect(url_for("loginPage"))
    
@app.route('/forgotpwd', methods=['GET', 'POST'])
@app.route('/forgotpwd/', methods=['GET', 'POST'])
def initialForgotPage():
    """
    forgot password page.
    """
    field = EmailField()
    if request.method == "POST":
        recipient_email = field.email.data
        user = User.query.filter_by(email=recipient_email).first()
        if isinstance(user, type(None)):
            alert_method.update(method=f"No Account found under {recipient_email}.")
            return redirect(url_for("loginPage"))
        reset_token = urlSerializer.dumps(recipient_email, salt="forgot-pass")
        reset_url = 'http://127.0.0.1:5000' + url_for("resetRequestRecieved", token=reset_token, email=recipient_email)
        reset_msg = Message('Reset Password', recipients=[recipient_email])
        reset_msg.body = f"""
        Dear User,
        You have requested to reset your password. Follow the link below to reset your password.
        Reset Password: {reset_url}
        """
        mail.send(reset_msg)
        alert_method.update(method=f"Reset Password Email has been sent.")
        return redirect(url_for('loginPage'))
    else:
        return render_template("forgot.html", field=field)
    
@app.route('/forgotpwd/<token>/<email>', methods=['GET', 'POST'])
@app.route('/forgotpwd/<token>/<email>/', methods=['GET', 'POST']) 
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
                alert_method.update(method="Password has been Successfully reset.")
            else:
                alert_method.update(method="The Requested Password is the same as the current password")
            return redirect(url_for('loginPage'))
        else:
            return render_template("forgotrecieved.html", form=form, token=token, email=email)
    
    except SignatureExpired:
        alert_method.update(method="Reset Link Expired. You must request to reset your password again")
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
    alert_method.update(method='Succesfully signed out')
    return redirect(url_for("loginPage"))
    
@app.route('/home')
@app.route('/home/')
@login_required
@roles_accepted('verified', 'unverified')
def homePage():
    """
    website homepage
    """
    alert_type = get_alert_type()
    return render_template("homepage.html", alert_type=alert_type)
    
@app.route('/about')
@app.route('/about/')
@login_required
@roles_accepted('verified', 'unverified')
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
        articles = Article.query.all()
        return render_template("articles/articlepage.html", articles=articles)
    else:
        return render_template("articles/articleform.html", form=form)
    
@app.route('/articles', methods=['GET', 'POST'])
@app.route('/articles/', methods=['GET', 'POST'])
@login_required
@roles_accepted('verified', 'unverified')
def article_home():
    try:
        articles = Article.query.all()
    except OperationalError:
        abort(400)
    return render_template("articles/articlepage.html", articles=articles)

@app.route('/articles/<string:id>')
@app.route('/articles/<string:id>/')
@login_required
@roles_accepted('verified', 'unverified')
@is_valid_article_page
def articlePage(id):
    try:
        article = Article.query.filter_by(id=id).first()
    except OperationalError:
        abort(404)
    return render_template('articles/articleviewpage.html', article=article)

@app.route('/contact', methods=['GET', 'POST'])
@app.route('/contact/', methods=['GET', 'POST'])
@login_required
@roles_accepted('verified', 'unverfied')
def contact_us():
    form = contactForm()
    if request.method == 'POST' and form.validate_on_submit():
        name = form.first_name.data + " " + form.last_name.data
        inquiry_selection = dict(form.inquiry_selection.choices).get(form.inquiry_selection.data)
        email = form.email.data
        tel = form.mobile.data
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
        return redirect(url_for('homePage'))
    else:
        return render_template('contactpage.html', form=form)
    
# ------------------ Website Starter ------------------
if __name__ == '__main__':
    print("[PRE-CONNECTING] Creating database if not exists")
    db.create_all()
    print("[PRE-CONNECTING] ........")
    print("[CONNECTING] Connecting to website...")
    app.run(debug=True)