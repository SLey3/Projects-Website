# Imports 
from flask import (
    Flask, render_template,
    redirect, request,
    url_for, flash
)
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField

from wtforms.validators import (
    InputRequired, Length,
    Email, DataRequired,
    EqualTo
)
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from datetime import timedelta
from flask_login import (
    LoginManager, login_required,
    UserMixin, login_user, logout_user,
    current_user
)

# app Config
app = Flask(__name__)
app.config["SECRET_KEY"] = "Kwl986"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["RECAPTCHA_PUBLIC_KEY"] = "6LfrfNgZAAAAAKzTPtlo2zh9BYXVNfoVzEHeraZM"
app.config["RECAPTCHA_PRIVATE_KEY"] = "6LfrfNgZAAAAAIFW8pX7L349lOaNam3ARg4nm1yP"
app.permanent_session_lifetime = timedelta(days=5)

# ------------------ app Config: SQLAlchemy Config ------------------
db = SQLAlchemy(app)

# ------------------ app Config: Flask_login Config ------------------
login_manager = LoginManager()
login_manager.init_app(app)


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
    name = StringField("name", validators=[DataRequired("Name Entry required"), Length(min=3, message="minimum length must be 3 characters")])
    email = StringField("email", validators=[DataRequired("Email Entry required"), Email("This must be an email", check_deliverability=True), 
                                             Length(min=3, max=50, message="Email length must be at most 50 characters")])
    password = PasswordField("password", validators=[DataRequired("Password field must not be blank"), Length(min=8, max=99,
                                                                                         message="length should be between 8-99 characters")])
    confirm_pass = PasswordField("confirm_pass", validators=[DataRequired("You must confirm the password."), EqualTo("password", 
                                                                        "Confirmation password must equal to the created password")])
    recaptcha = RecaptchaField()

# ------------------ User class ------------------
class User(db.Model, UserMixin):
    """
    User Model
    """
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100))
    username = db.Column("email", db.String(100), unique=True)
    password = db.Column("password", db.String(255))

# ------------------ External Resources
@login_manager.user_loader
def load_user(user_id):
    """
    Gets the User
    """
    return User.query.get(int(user_id))

# ------------------ web pages ------------------

@app.route('/', methods=["GET", "POST"])
def loginPage():
    """
    main front page
    """
    form = loginForm()
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
            return render_template("loginpage.html", form=form)

@app.route('/register', methods=['GET', 'POST'])
def registerPage():
    form = registerForm()
    if request.method == "POST" and form.validate_on_submit():
        new_user = User(
            name=request.form.get("name"),
            username=request.form.get("email"),
            password=sha256_crypt.encrypt(request.form.get("password"))
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration Succesful", 'success')
        return redirect(url_for("loginPage"))
    else:
        return render_template("registerpage.html", form=form)
    
@app.route('/signout')
def signOut():
    """
    Signs out of the site
    """
    logout_user()
    form = loginForm()
    flash("Succesfully signed out", 'success')
    return redirect(url_for("loginPage"))
    
@app.route('/home')
@login_required
def homePage():
    """
    website homepage
    """
    return redirect(url_for("loginPage"))
    
@app.route('/about')
@login_required
def aboutPage():
    return redirect(url_for("loginPage"))
    
# ------------------ Website Starter ------------------
if __name__ == '__main__':
    print("[PRE-CONNECTING] Creating database if not exists")
    db.create_all()
    print("[PRE-CONNECTING] ........")
    print("[CONNECTING] Connecting to website...")
    app.run(debug=True)