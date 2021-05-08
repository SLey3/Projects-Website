# ------------------ Imports ------------------
from flask import (
    Blueprint, render_template,
    redirect, request,
    url_for, abort, current_app
)
try:
    from flask_sqlalchemy.orm.session import Session as SQLSession
except ModuleNotFoundError:
    from sqlalchemy.orm.session import Session as SQLSession
from flask_mail import Message
from ProjectsWebsite.util import (
    is_valid_article_page, formatPhoneNumber, DateUtil,
    current_user, login_user, logout_user, token_auth_required, 
    roles_required, roles_accepted, unverfiedLogUtil
)
from ProjectsWebsite.util.mail import automatedMail, formatContact
from ProjectsWebsite.util.helpers import date_re
from ProjectsWebsite.util.utilmodule import alert
from ProjectsWebsite.modules import (
    db, img_set, mail, login_manager,
    guard
)
from ProjectsWebsite.forms import (
    loginForm, registerForm,
    articleForm, contactForm,
    forgotForm, forgotRequestForm
)
from ProjectsWebsite.database.models import (
    Article, User, Role, user_datastore
)
from io import open as iopen
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from sqlalchemy.exc import OperationalError
from passlib.hash import sha512_crypt
from datetime import datetime
from traceback import format_exc
import base64
import os


# ------------------ Blueprint Config ------------------
main_app = Blueprint('main_app', __name__, static_folder='static', template_folder='templates/public')


# ------------------  SQLAlchemy Session Config ------------------
sql_sess = SQLSession(autoflush=False)

# ------------------ Application Import ------------------
from ProjectsWebsite import app

# ------------------ Serializer config ------------------
urlSerializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

# ------------------ unverLog init ------------------
unverlog = unverfiedLogUtil()


# ------------------ LoginManaer: User Resource ------------------
@login_manager.user_loader
def load_user(user_id):
    """
    Gets the User
    """
    return User.identify(int(user_id))

# ------------------ web pages ------------------
@main_app.route('/login/', methods=['GET', 'POST'])
def loginPage():
    """
    main front page
    """
    form = loginForm()
    
    alert_dict = alert.getAlert()
    
    if request.method == 'POST':
        user = guard.authenticate(form.username.data, form.password.data)
        if user:
            token = guard.encode_jwt_token(user)
            login_user(token, user)
            return redirect(url_for(".homePage"))
        error = "Invalid Email or Password"
        return render_template("public/loginpage.html", form=form, error=error, alert_msg=alert_dict['Msg'], alert_type=alert_dict['Type'])
    else:
        if current_user.is_authenticated:
            return redirect(url_for('.homePage'))
        return render_template("public/loginpage.html", form=form, alert_msg=alert_dict['Msg'], alert_type=alert_dict['Type'])

@main_app.route('/register/', methods=['GET', 'POST'])
def registerPage():
    """
    Registration Page
    """
    global email
    form = registerForm()
    if request.method == 'POST':
        with sql_sess.no_autoflush:
            user_datastore.find_or_create_role('admin')
            user_datastore.find_or_create_role('member')
            user_datastore.find_or_create_role('unverified')
            user_datastore.find_or_create_role('verified')
        current_date = datetime.now()
        new_user = user_datastore.create_user(
            name=form.name.data.capitalize(),
            username=form.email.data.lower(),
            email=form.email.data.lower(),
            hashed_password=guard.hash_password(form.password.data),
            created_at=f'{current_date.month}/{current_date.day}/{current_date.year}',
            blacklisted=False,
            roles=['member', 'unverified']
        )
        user_datastore.commit()
        def yield_email(email):
            yield email
        email = yield_email(form.email.data.lower())
        token = urlSerializer.dumps(form.email.data, salt='email-confirm')
        verify_msg = Message('Confirm Account', recipients=[form.email.data])
        confirm_link = 'http://127.0.0.1:5000' + url_for(".confirmation_recieved", token=token, external=True)
        verify_msg.html = automatedMail(form.name.data, f'''
                                        Thank you for registering! In order to complete the registration you must click on the link below. <br>
                                        Link will expire in <b>30</b> minutes after this email has been sent. <br>
                                        Link: <a href="{confirm_link}">Confirm Account</a>''')
        mail.send(verify_msg)
        alert.setAlert('success', 'Registration Succesful. Check your email for confirmation link.')
        unverlog.addContent(form.email.data.lower(), token, mode="r+")  
        return redirect(url_for(".homePage"))
    else:
        return render_template("public/registerpage.html", form=form)
    
@main_app.route('/confirm_recieved/<token>/')  
def confirmation_recieved(token):
    """
    Confirmation and account creation page
    :param token: Email token
    """
    global email
    email = "".join(email)
    try:
        urlSerializer.loads(token, salt="email-confirm", max_age=3600/2)
        user_datastore.remove_role_from_user(User.lookup(email), 'unverified')
        user_datastore.add_role_to_user(User.lookup(email), "verified")
        user_datastore.commit()
        unverlog.removeContent(email, 'r+')
        alert.setAlert('success', 'Email Verified')
        return redirect(url_for(".homePage"))
    except SignatureExpired:
        notice_user = User.lookup(email)
        notice_msg = Message('Account Validation Warning', recipients=[notice_user.email])
        notice_msg.html = automatedMail(notice_user.name, 
                                        f'''
                                        We regret to inform you that your account may expire at around 0 to 1 hour due to confirmation token have expired. <br>
                                        Contact support if you want to make sure that your account won't automatically be deleted at: {url_for('.contact_us')} (<i>Notice:</i>
                                        <b>Support may be offline at any given time and may not reply fast enough. If this is the case and the 0 to 1 hour period is up then create an account again at:</b><a href="{url_for(".registerPage")}">Register</a>").
                                        ''')
        mail.send(notice_msg)
        return redirect(url_for(".homePage"))
    
@main_app.route('/login/forgotpwd/', methods=['GET', 'POST'])
def initialForgotPage():
    """
    forgot password page.
    """
    form = forgotRequestForm()
    if request.method == "POST":
        recipient_email = form.email.data
        user = User.lookup(form.email.data)
        if isinstance(user, type(None)):
            if recipient_email != '' and form.submit.data == True:
                alert.setAlert('warning', f"No Account found under {recipient_email}.")
                return redirect(url_for(".loginPage"))
            elif recipient_email == '' and form.back_button.data:
                return redirect(url_for('.loginPage'))
        if not form.submit.data and form.back_button.data:
            return redirect(url_for('loginPage')) 
        reset_token = urlSerializer.dumps(recipient_email, salt="forgot-pass")
        reset_url = 'http://127.0.0.1:5000' + url_for("resetRequestRecieved", token=reset_token, email=recipient_email)
        reset_msg = Message('Reset Password', recipients=[recipient_email])
        reset_msg.html = automatedMail(user.name, 
                                f'''You have requested to reset your password. Follow the link below to reset your password.
                                    <br> Reset Password: {reset_url}''')
        mail.send(reset_msg)
        alert.setAlert('success', 'Reset Password Email has been sent.')
        return redirect(url_for('.homePage'))
    else:
        return render_template("public/forgot.html", field=form)
    
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
            replacementPassword = guard.hash_password(form.confirm_new_password.data)
            user = User.lookup(email)
            if not guard.authenticate(user, form.confirm_new_password.data):
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
        return redirect(url_for(".loginPage"))

@main_app.route('/signout/')
@token_auth_required
def signOut():
    """
    Signs out of the site
    """
    logout_user()
    alert.setAlert('success', 'Successfully signed out')
    return redirect(url_for(".homePage"))
    
@main_app.route('/')
def homePage():
    """
    website homepage
    """
    alert_dict = alert.getAlert()
    return render_template("public/homepage.html", alert_msg=alert_dict['Msg'], alert_type=alert_dict['Type'])

@main_app.route('/home/')
def redirectToHomePage():
    """
    redirects to homepage
    """
    return redirect(url_for('.homePage'))
    
@main_app.route('/about/')
def aboutPage():
    return render_template('public/aboutpage.html')

@main_app.route('/articles/create_article/', methods=['GET', 'POST'])
@roles_accepted("admin", "editor")
@token_auth_required
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
        creation_date = date_util.datetimeSubDate(date_re)
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
    
@main_app.route('/articles/', methods=['GET', 'POST'])
def article_home():
    try:
        articles = Article.query.all()
    except Exception:
        exc = format_exc()
        print(exc)
    return render_template("public/articles/articlepage.html", articles=articles)

@main_app.route('/articles/<string:id>/')
@is_valid_article_page
def articlePage(id):
    try:
        article = Article.query.filter_by(id=id).first()
    except Exception:
        exc = format_exc()
        print(exc)
    return render_template('articles/articleviewpage.html', article=article)

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
        mail_msg.html = formatContact(name=name, inquiry_selection=inquiryselection, email=email, tel=tel, msg=msg)
        mail.send(mail_msg)
        alert.setAlert('info', 'Contact Message has been Sent. Please wait for a responce from support team.')
        return redirect(url_for('.homePage'))
    else:
        return render_template('public/contactpage.html', form=form)

@main_app.route('/home/admin/')   
@roles_required('admin', 'verified')
def adminPage():
    """
    Administrator Page
    """
    return redirect(url_for("admin.adminHomePage"))