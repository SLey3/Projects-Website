# Imports 
from flask import (
    Flask, render_template,
    redirect, request,
    url_for, session,
    flash
)
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import (
    StringField, PasswordField
)
from wtforms.validators import (
    InputRequired, Length,
    Email, DataRequired,
    EqualTo
)
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from datetime import timedelta

# app Config
app = Flask(__name__, template_folder='../templates')
app.config["SECRET_KEY"] = "Kwl986"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["RECAPTCHA_PUBLIC_KEY"] = "6LfrfNgZAAAAAKzTPtlo2zh9BYXVNfoVzEHeraZM"
app.config["RECAPTCHA_PRIVATE_KEY"] = "6LfrfNgZAAAAAIFW8pX7L349lOaNam3ARg4nm1yP"
app.permanent_session_lifetime = timedelta(days=5)
db = SQLAlchemy(app)

# Forms
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
    name = StringField("name", validators=[DataRequired("Name Entry required"), Length(min=3, message="minimum length must be 3 characters")])
    email = StringField("email", validators=[DataRequired("Email Entry required"), Email("This must be an email", check_deliverability=True), 
                                             Length(min=3, max=50, message="Email length must be at most 50 characters")])
    password = PasswordField("password", validators=[DataRequired("Password field must not be blank"), Length(min=8, max=99,
                                                                                         message="length should be between 8-99 characters")])
    confirm_pass = PasswordField("confirm_pass", validators=[DataRequired("You must confirm the password."), EqualTo("password", 
                                                                        "Confirmation password must equal to the created password")])
    recaptcha = RecaptchaField()

# User class
class userData(db.Model):
    """
    User Model
    """
    ID = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100))
    email = db.Column("email", db.String(100), unique=True)
    # password = db.Column("password", db.String(100))
    
    def __init__(self, name, email, password=None):
        self.name = name
        self.email = email
        # self.password = password
    

# web pages

@app.route('/', methods=["GET", "POST"])
def loginPage():
    """
    main front page
    """
    form = loginForm()
    if request.method == "POST" and form.validate_on_submit():
        session.permanent = True
        username = request.form["username"]
        session['user'] = username
        return redirect(url_for("usr", usr=username))
    else:
        if "user" in session:
            return redirect(url_for("homePage"))
        else:
            return render_template("loginpage.html", msg="Login Page", form=form)

@app.route('/register', methods=['GET', 'POST'])
def registerPage():
    form = registerForm()
    if request.method == "POST" and form.validate_on_submit():
        return redirect(url_for("loginPage"))
    else:
        return render_template("registerpage.html", form=form)
    
@app.route('/signout')
def signOut():
    """
    Signs out of the site
    """
    session.pop("user", None)
    return redirect(url_for("loginPage"))
    
@app.route('/<usr>')
def usr(usr):
    """
    Automatically redirects user to homePage
    """
    return redirect(url_for("homePage"))
    
@app.route('/home')
def homePage():
    """
    website homepage
    """
    if "user" in session:
        return render_template("homepage.html", msg="Hello World")
    else:
        return redirect(url_for("loginPage"))
    
@app.route('/about')
def aboutPage():
    if "user" in session:
        return render_template("aboutpage.html")
    else:
        return redirect(url_for("loginPage"))
    
if __name__ == '__main__':
    print("[PRE-CONNECTING] Creating database if not exists")
    db.create_all()
    print("[PRE-CONNECTING] ........")
    print("[CONNECTING] Connecting to website...")
    app.run(debug=True)