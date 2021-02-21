# ------------------ Imports ------------------
from flask import (
    Blueprint, render_template,
    redirect, request,
    url_for, abort, jsonify
)
try:
    from flask_sqlalchemy.orm.session import Session as SQLSession
except ModuleNotFoundError:
    from sqlalchemy.orm.session import Session as SQLSession
from flask_login import (
    LoginManager, login_user, 
    logout_user, current_user
)
from flask_mail import Mail, Message
from flask_uploads import UploadSet, IMAGES
from flask_security import (
    Security, SQLAlchemyUserDatastore, 
    roles_accepted, roles_required, 
    login_required
)
from flask_assets import Environment, Bundle
from src.util import (
    AlertUtil, is_valid_article_page, formatPhoneNumber, DateUtil
)
from src.util.helpers import EMAILS, date_re
from src.forms import (
    loginForm, registerForm,
    articleForm, contactForm,
    forgotForm, forgotRequestForm
)
from src.database.models import (
    db, Article, User, Role
)
from io import open as iopen
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from sqlalchemy.exc import OperationalError
from passlib.hash import sha512_crypt
from datetime import datetime
from src import app
import base64
import os


# ------------------ Blueprint Config ------------------
main_app = Blueprint('main_app', __name__, static_folder='static', template_folder='templates/public')


# ------------------ Library Configs ------------------
img_set = UploadSet('images', IMAGES)

mail = Mail()

login_manager = LoginManager()

assets = Environment()

alert = AlertUtil()

security = Security()

# ------------------  SQLAlchemy Session Config ------------------
sql_sess = SQLSession(autoflush=False)

# ------------------ Serializer config ------------------
urlSerializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
   
# ------------------ Static Files Bundles ------------------ 

js_main_bundle = Bundle('js/main/src/confirm.js', 'js/main/src/pass.js', 'js/main/src/novalidate.js',
                   filters='jsmin', output="js/main/dist/main.min.js") 

edit_profile_js_bundle = Bundle('js/ext/admin/accounts/edit_profile/src/element.js', 'js/ext/admin/accounts/edit_profile/src/navalign.js',
                                filters='jsmin', output='js/ext/admin/accounts/edit_profile/dist/index.min.js')

alert_css_bundle = Bundle('styles/alert_css/src/box.css', 'styles/alert_css/src/error.css', 
                    'styles/alert_css/src/info.css', 'styles/alert_css/src/success.css',
                    'styles/alert_css/src/warning.css', filters='cssmin', 
                    output='styles/alert_css/dist/alerts.min.css')

admin_home_css_bundle = Bundle('styles/admin/index/src/index.css', 'styles/admin/util/scrollbar/scrollbar.css',
                               'styles/admin/util/navbar/navbar.css', 'styles/admin/util/management/management.css', 
                               filters='cssmin', output='styles/admin/index/dist/index.min.css')

admin_main_accounts_css_bundle = Bundle('styles/admin/accounts/main/src/index.css', 'styles/admin/util/scrollbar/scrollbar.css',
                                  'styles/admin/util/navbar/navbar.css', 'styles/admin/util/management/management.css',
                                  filters='cssmin', output='styles/admin/accounts/main/dist/index.min.css')

admin_edit_profile_accounts_css_bundle = Bundle('styles/admin/accounts/edit_profiles/src/edit_profile.css', 'styles/admin/util/scrollbar/scrollbar.css',
                                                'styles/admin/util/navbar/navbar.css', 'styles/admin/util/management/management.css',
                                                filters='cssmin', output='styles/admin/accounts/edit_profiles/dist/edit_profile.min.css')

# ------------------  Bundle Config: Registration ------------------ 
assets.register('main__js', js_main_bundle)

assets.register('edit_prof_main_js', edit_profile_js_bundle)
  
assets.register('alert__css', alert_css_bundle)

assets.register('admin_dashboard_css', admin_home_css_bundle)

assets.register('admin_main_accounts_css', admin_main_accounts_css_bundle)

assets.register('admin_edit_accounts_css', admin_edit_profile_accounts_css_bundle)

# ------------------ UserDatastore Config ------------------
    
user_datastore = SQLAlchemyUserDatastore(db, User, Role)

# ------------------ LoginManaer: User Resource ------------------
@login_manager.user_loader
def load_user(user_id):
    """
    Gets the User
    """
    return User.query.get(int(user_id))

# ------------------ web pages ------------------

@main_app.route('/login', methods=["GET", "POST"])
@main_app.route('/login/', methods=["GET", "POST"])
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
                return jsonify(user.to_json())
        error = "Invalid Email or Password"
        return render_template("public/loginpage.html", form=form, error=error, alert_msg=alert_dict['Msg'], alert_type=alert_dict['Type'])
    else:
        if current_user.is_authenticated:
            return redirect(url_for("homePage"))
        else:
            return render_template("public/loginpage.html", form=form, alert_msg=alert_dict['Msg'], alert_type=alert_dict['Type'])

@main_app.route('/register', methods=['GET', 'POST'])
@main_app.route('/register/', methods=['GET', 'POST'])
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
        current_date = datetime.now()
        user_datastore.create_user(
            name=form.name.data.capitalize(),
            email=form.email.data.lower(),
            password=sha512_crypt.hash(form.password.data),
            created_at=f'{current_date.month}/{current_date.day}/{current_date.year}',
            blacklisted=False,
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
        return redirect(url_for("homePage"))
    else:
        return render_template("public/registerpage.html", form=form)
    
@main_app.route('/confirm_recieved/<token>')  
@main_app.route('/confirm_recieved/<token>/')  
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
        return redirect(url_for("homePage"))
    except SignatureExpired:
        email_string = EMAILS.pop(0)
        User.query.filter_by(email=email_string).delete()
        db.session.commit()
        alert.setAlert('error', 0)
        return redirect(url_for("homePage"))
    
@main_app.route('/login/forgotpwd', methods=['GET', 'POST'])
@main_app.route('/login/forgotpwd/', methods=['GET', 'POST'])
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
        return redirect(url_for('homePage'))
    else:
        return render_template("public/forgot.html", field=form)
    
@main_app.route('/login/forgotpwd/<token>/<email>', methods=['GET', 'POST'])
@main_app.route('/login/forgotpwd/<token>/<email>/', methods=['GET', 'POST']) 
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
            return render_template("public/forgotrecieved.html", form=form, token=token, email=email)
    
    except SignatureExpired:
        alert.setAlert('error', 1)
        return redirect(url_for("loginPage"))
    
@main_app.route('/signout')
@main_app.route('/signout/')
@login_required
def signOut():
    """
    Signs out of the site
    """
    logout_user()
    form = loginForm()
    alert.setAlert('success', 'Succesfully signed out')
    return redirect(url_for("homePage"))
    
@main_app.route('/')
@main_app.route('/')
def homePage():
    """
    website homepage
    """
    alert_dict = alert.getAlert()
    return render_template("public/homepage.html", alert_msg=alert_dict['Msg'], alert_type=alert_dict['Type'])

@main_app.route('/home')
@main_app.route('/home/')
def redirectToHomePage():
    """
    redirects to homepage
    """
    return redirect(url_for('homePage'))
    
@main_app.route('/about')
@main_app.route('/about/')
def aboutPage():
    return render_template('public/aboutpage.html')

@main_app.route('/articles/create_article', methods=['GET', 'POST'])
@main_app.route('/articles/create_article/', methods=['GET', 'POST'])
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
        date_util = DateUtil(current_date)
        creation_date = date_util.subDate(date_re)
        del current_date
        body = request.form["editordata"]         
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
        return redirect(url_for(".homePage"))
    else:
        return render_template("public/articles/articleform.html", form=form)
    
@main_app.route('/articles', methods=['GET', 'POST'])
@main_app.route('/articles/', methods=['GET', 'POST'])
def article_home():
    try:
        articles = Article.query.all()
    except OperationalError:
        abort(400)
    return render_template("public/articles/articlepage.html", articles=articles)

@main_app.route('/articles/<string:id>')
@main_app.route('/articles/<string:id>/')
@is_valid_article_page
def articlePage(id):
    try:
        article = Article.query.filter_by(id=id).first()
    except OperationalError:
        abort(404)
    return render_template('articles/articleviewpage.html', article=article)

@main_app.route('/contact', methods=['GET', 'POST'])
@main_app.route('/contact/', methods=['GET', 'POST'])
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
        return render_template('public/contactpage.html', form=form)

@main_app.route('/home/admin')
@main_app.route('/home/admin/')   
@roles_required('admin', 'verified')
def adminPage():
    """
    Administrator Page
    """
    return redirect(url_for("admin.adminHomePage"))