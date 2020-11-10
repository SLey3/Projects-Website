# ------------------ Imports ------------------
from flask import (
    Flask, render_template,
    redirect, request,
    url_for, flash
)
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import (
    StringField, PasswordField, 
    TextAreaField, SelectField
)
from wtforms.fields.html5 import TelField

from wtforms.validators import (
    InputRequired, Length,
    Email, DataRequired,
    EqualTo
)
from flask_sqlalchemy import SQLAlchemy
try:
    from flask_sqlalchemy.orm.session import Session
except ModuleNotFoundError:
    from sqlalchemy.orm.session import Session
from passlib.hash import sha256_crypt
from datetime import timedelta
from flask_login import (
    LoginManager, login_required,
    login_user, logout_user,
    current_user
)
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_admin import Admin, expose, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_security import (
    Security, SQLAlchemyUserDatastore,
    UserMixin, RoleMixin, roles_accepted,
    roles_required
)
from dashboard import dash
# from flask_pymongo import PyMongo

# ------------------ app Config ------------------
app = Flask(__name__, template_folder="templates/public")
app.config["SECRET_KEY"] = "Kwl986"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["MONGO_URI"] = "mongodb+srv://SergioLey:admin123456@project-mikeyankeepapar.hddfz.mongodb.net/users.sqlite?retryWrites=true&w=majority"
app.config["RECAPTCHA_PUBLIC_KEY"] = "6LfrfNgZAAAAAKzTPtlo2zh9BYXVNfoVzEHeraZM"
app.config["RECAPTCHA_PRIVATE_KEY"] = "6LfrfNgZAAAAAIFW8pX7L349lOaNam3ARg4nm1yP"
app.config["MAIL_DEFAULT_SENDER"] = "noreplymyprojectsweb@gmail.com"
app.config["MAIL_USERNAME"] = "noreplymyprojectsweb@gmail.com"
app.config["MAIL_PASSWORD"] = "hFb5b4UcwovqTshinAv6exVHY2pUT4N5lY77XRVEfmPFaY98nA9NOsQULJY2IVR66YFIMH6dgtdx9o1VoLLBW4YYrjcjRC10a3v"
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USE_TLS "] = False
app.permanent_session_lifetime = timedelta(days=5)
app.register_blueprint(dash)

# ------------------ app Config: SQLAlchemy / PyMongo Config ------------------
db = SQLAlchemy(app)

sql_sess = Session(autoflush=False)

# --------- Currently disabled for if sqlalchemy needs to be replaced

# mongo = PyMongo(app)

# ------------------ app Config: Flask_login Config ------------------
login_manager = LoginManager()
login_manager.init_app(app)

# ------------------ app Config: Flask_mail Config ------------------
mail = Mail()
mail.init_app(app)

s = URLSafeTimedSerializer(app.config["SECRET_KEY"])

# ------------------ app Config: Admin Config ------------------
admin = Admin(app, template_mode="bootstrap4")

# ------------------ Forms ------------------
class loginForm(FlaskForm):
    """
    website login Form for loginpage.html
    """
    username = StringField("username", validators=[
        InputRequired(message="Username field should not be blank"), 
        Length(min=3, max=50, message="Email length must be at most 50 characters"), Email(message="This must be an Email", check_deliverability=True)])
    password = PasswordField("password", validators=[InputRequired("Password field should not be blank"), 
                                                     Length(min=8, max=99, message='''length should be between 8-99 characters''')])
    
class registerForm(FlaskForm):
    """
    registration form for website
    """
    name = StringField("name", validators=[DataRequired("Name Entry required"), Length(min=3, max=10, message="Name length must be between 3-10 characters")], 
                       render_kw={'placeholder':'Name'})
    email = StringField("email", validators=[DataRequired("Email Entry required"), Email("This must be an email", check_deliverability=True), 
                                             Length(min=3, max=50, message="Email length must be at most 50 characters")], 
                                            render_kw={'placeholder':'Email'})
    password = PasswordField("password", validators=[DataRequired("Password field must not be blank"), Length(min=8, max=99,
                                                                                         message="length should be between 8-99 characters")],
                                                                                        render_kw={'placeholder':'Password'})
    confirm_pass = PasswordField("confirm_pass", validators=[DataRequired("You must confirm the password."), EqualTo("password", 
                                                                        "Confirmation password must equal to the created password")],
                                                                        render_kw={'placeholder':'confirm_pass'})
    recaptcha = RecaptchaField()
    
    
class articleForm(FlaskForm):
    """
    article form for website
    """
    title = StringField("title", validators=[DataRequired("Title Entry required"), Length(min=5, max=100, message="Title must be between 5-100 characters")], 
                        render_kw={"placeholder":"Enter title"})
    
    short_desc = StringField("short_description", validators=[DataRequired("Short Description Entry required"), 
                                                              Length(min=15, max=30, message="Short Description must have between 15-30 characters")], 
                             render_kw={'placeholder':"Enter Short Description"})
    
    body = TextAreaField("body", validators=[DataRequired("Body Entry Required"), Length(min=50, message="Body must have minimum 50 characters")], 
                        render_kw={"placeholder":"Enter Body Text", 'class':'editor'})

class contactForm(FlaskForm):
    """
    Contact Us form
    """
    first_name = StringField("first_name", validators=[DataRequired("First name Entry required"), Length(min=3, max=9, message="Name length must be between 3-9 characters")], 
                             render_kw={'class':'form-control'})
    
    last_name = StringField("last_name", validators=[DataRequired("First name Entry required"), Length(min=2, max=19, message="Name length must be between 2-19 characters")],
                            render_kw={'class':'form-control'})
    
    inquiry_selection = SelectField('inquiry', choices=[('General', 'General Inquiry'), ('Security', 'Security Inquiry'), ('Article', 'Aritle Inquiry'), ('Other Inquiry', 'Other')],
                                    validators=[DataRequired("Inquiry Choice Required")], render_kw={'class':'form-control'})
    
    email = StringField("email", validators=[DataRequired("Email Entry required"), Email("This must be an email", check_deliverability=True),
                                            Length(min=3, max=50, message="Email length must be at most 50 characters")],
                        render_kw={'class':'form-control'})
    
    mobile = TelField("mobile_number", validators=[DataRequired("Mobile Field Required")], render_kw={'class':'form-control'})
    
    message = TextAreaField("message", validators=[Length(min=50, message="Body must have minimum 50 characters")], render_kw={'cols':30, 'rows':10, 'class':'form-control'})
    
    
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
    username = db.Column("email", db.String(100), unique=True)
    password = db.Column("password", db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
        
    def __repr__(self):
        return f"Name: {self.name}"
    
    
# class Article(db.Model):
#     """
#     Article Model
#     """
#     id = db.Column("id", db.Integer, primary_key=True)
#     title = db.Column("title", db.String(100))
#     body = db.Column("body", db.String(900))

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

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


# ------------------ External Resources: Global Constants ------------------

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
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if sha256_crypt.verify(form.password.data, user.password):
                login_user(user)
                return redirect(url_for("homePage"))
        error = "Invalid Email or Password"
        return render_template("loginpage.html", form=form, error=error)
    else:
        if current_user.is_authenticated:
            return redirect(url_for("homePage"))
        else:
            return render_template("loginpage.html", form=form, alert_type=alert_type)

@app.route('/register', methods=['GET', 'POST'])
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
            name=request.form.get("name"),
            username=request.form.get("email"),
            password=sha256_crypt.hash(request.form.get("password")),
            roles=['admin', 'verified']
        )
        db.session.commit()
        EMAILS.append(form.email.data)
        token = s.dumps(form.email.data, salt='email-confirm')
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
def confirmation_recieved(token):
    """
    Confirmation and account creation page
    :param token: Email token
    """
    try:
        email = s.loads(token, salt="email-confirm", max_age=3600/2)
        EMAILS.clear()
        alert_method.update(method='Email Verified')
        return redirect(url_for("loginPage"))
    except SignatureExpired:
        email_string = EMAILS.pop(0)
        User.query.filter_by(username=email_string).delete()
        db.session.commit()
        alert_method.update(method='Confirmation link expired. You must Register again')
        return redirect(url_for("loginPage"))
    
@app.route('/signout')
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
@login_required
@roles_accepted('verified', 'unverified')
def homePage():
    """
    website homepage
    """
    alert_type = get_alert_type()
    return render_template("homepage.html", alert_type=alert_type)
    
@app.route('/about')
@login_required
@roles_accepted('verified', 'unverified')
def aboutPage():
    return redirect(url_for("loginPage"))

@app.route('/articles/create_article', methods=['GET', 'POST'])
@login_required
@roles_accepted('admin', 'editor')
def articleCreation():
    form = articleForm()
    if request.method == "POST" and form.validate_on_submit():
        pass
        # article = Article(
        #     title=form.title.data
        #     body=form.body.data
        # )
        # db.session.add(article)
        # db.commit()
    else:
        return render_template("articles/articleform.html", form=form)
    
@app.route('/articles')
@login_required
@roles_accepted('verified', 'unverified')
def article_home():
    return render_template("articles/articlepage.html")

@app.route('/contact', methods=['GET', 'POST'])
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