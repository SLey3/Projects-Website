# Imports 
from flask import (
    Flask, render_template,
    redirect, request,
    url_for, session,
    flash
)
from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField
)
from wtforms.validators import (
    InputRequired, Length,
    Email
)
from passlib.hash import sha256_crypt
from datetime import timedelta

# app Config
app = Flask(__name__, template_folder='../templates')
app.config["SECRET_KEY"] = "Kwl986"
app.permanent_session_lifetime = timedelta(days=5)

# Forms
class loginForm(FlaskForm):
    """
    website login Form for loginpage.html
    """
    username = StringField("username", validators=[
        InputRequired(message="Username field should not be blank"), 
        Length(min=3, max=50, message="Email length must be at most 50 characters"), Email(message="This must be an Email", check_deliverability=True)])
    password = PasswordField("password", validators=[InputRequired("Password field should not be blank"), 
                                                     Length(min=15, max=99, message='''Minimum length should 
                                                            be 15 characters and maximum length should be 99 characters.''')])

# web pages

@app.route('/', methods=["GET", "POST"])
def loginPage():
    """
    main front page
    """
    if request.method == "POST":
        session.permanent = True
        username = request.form["username"]
        session['user'] = username
        return redirect(url_for("usr", usr=username))
    else:
        if "user" in session:
            return redirect(url_for("homePage"))
        else:
            form = loginForm()
            return render_template("private/loginpage.html", msg="Login Page", form=form)

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
        return render_template("public/homepage.html", msg="Hello World")
    else:
        return redirect(url_for("loginPage"))