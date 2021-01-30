# ------------------ Imports ------------------
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import (
    StringField, PasswordField, 
    TextAreaField, SelectField,
    SubmitField, BooleanField
)
from wtforms.fields.html5 import TelField, SearchField
from flask_uploads import UploadSet, IMAGES
from src.forms.validators import *
from src.forms.field import ButtonField

# ------------------ img_set Config ------------------
img_set = UploadSet('images', IMAGES)

# ------------------ Forms------------------
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
    email = StringField("email",  validators=[DataRequired("Email Entry required"), Email("This must be an email", check_deliverability=True), 
                                             Length(min=3, max=50, message="Email length must be at most 50 characters")], 
                                            render_kw={'placeholder':'Email'})
    password = PasswordField("password", id="password", validators=[DataRequired("Password field must not be blank"), Length(min=8, max=99,
                                                                                         message="length should be between 8-99 characters")],
                                                                                        render_kw={'placeholder':'Password'})
    confirm_pass = PasswordField("confirm_pass", id="confirm_pass", validators=[DataRequired("You must confirm the password."), EqualTo("password", 
                                                                        "Confirmation password must equal to the created password")],
                                                                        render_kw={'placeholder':'confirm_pass'})
    recaptcha = RecaptchaField()
    
class articleForm(FlaskForm):
    """
    article form for website
    """
    title = StringField("title", validators=[DataRequired("Title Entry required"), Length(min=5, max=100, message="Title must be between 5-100 characters")], 
                        render_kw={"placeholder":"Enter title"})
    
    author = StringField("author", validators=[DataRequired("Author Entry required"), Length(min=3, max=100, message="Name must be between 3-100")],
                         render_kw={"placeholder":"Enter Authors name"})
    
    short_desc = StringField("short_description", validators=[DataRequired("Short Description Entry required")], 
                             render_kw={'placeholder':"Enter Short Description"})
    front_image = FileField('front_img', id='front-image', validators=[FileAllowed(img_set, "Images only")])

class contactForm(FlaskForm):
    """
    Contact Us form
    """
    first_name = StringField("first_name", validators=[DataRequired("First name Entry required"), Length(min=3, max=9, message="Name length must be between 3-9 characters")], 
                             render_kw={'class':'form-control'})
    
    last_name = StringField("last_name", validators=[DataRequired("First name Entry required"), Length(min=2, max=19, message="Name length must be between 2-19 characters")],
                            render_kw={'class':'form-control'})
    
    inquiry_selection = SelectField('inquiry', choices=[('General', 'General Inquiry'), ('Security', 'Security Inquiry'), ('Article', 'Article Inquiry'), ('Other Inquiry', 'Other')],
                                    validators=[DataRequired("Inquiry Choice Required")], render_kw={'class':'form-control'})
    
    email = StringField("email", validators=[DataRequired("Email Entry required"), Email("This must be an email", check_deliverability=True),
                                            Length(min=3, max=50, message="Email length must be at most 50 characters")],
                        render_kw={'class':'form-control'})
    
    mobile = TelField("mobile_number", validators=[DataRequired("Mobile Field Required"), ValidatePhone()], render_kw={'class':'form-control'})
    
    message = TextAreaField("message", validators=[Length(min=50, message="Body must have minimum 50 characters")], render_kw={'cols':30, 'rows':10, 'class':'form-control'})
    
class forgotForm(FlaskForm):
    """
    Password change form for forgot password
    """
    new_password = PasswordField("password", id="password", validators=[DataRequired("Password field Entry required."),  Length(min=8, max=99,
                                message="length should be between 8-99 characters")], render_kw={'placeholder':'New Password'})
    
    confirm_new_password = PasswordField("confirm_new_password", id="confirm_pass", validators=[DataRequired("Password Confirmation Required"), EqualTo("new_password", "Passwords do not match.")],
                                         render_kw={'placeholder':'Confirm Password'})
    
class forgotRequestForm(FlaskForm):
    """
    Creates the Initial Forgot Request Form
    """
    email = StringField('email', validators=[DataRequired("Email Entry required"), Email("This must be an email", check_deliverability=True),
                                            Length(min=3, max=50, message="Email length must be at most 50 characters")], 
                        render_kw={"placeholder": "Enter Email"})
    
    submit = SubmitField('Submit', id='sbmt-btn', render_kw={'value':'Send'})
    
    back_button = ButtonField('Back to Login', id='btn-redirect', render_kw={'href': '/', 'onclick':'NoValidateInput()'})
    
class AccountManegementForms:
    """
    Forms for account Mangement Admin dashboard
    """
    class tableSearchForm(FlaskForm):
        """
        Creates Search Input
        """
        command = SearchField('tbl search', id="table-search", render_kw={'class':'tbl-srch', 'placeholder':'Search By Name', 'autocomplete':'off'})
        
    class adminUserInfoForm(FlaskForm):
        """
        Creates Info Ediit form Inputs
        """
        name = StringField('Name', id='edit-name-input', validators=[DataRequired("Field may not be blank"), Length(min=3, max=10, message="Name length must be between 3-10 characters")],
                           render_kw={'placeholder':'Edit Name...', 'class':'name-input'})
        
        name_sbmt = SubmitField('Submit', id='name-sbmt-btn', render_kw={'value':'Submit', 'class':'name-sbmt-btn'})
        
        email = StringField('Email', id='edit-email-input', validators=[DataRequired("Field may not be blank"), Email("This must be an email", check_deliverability=True), 
                                             Length(min=3, max=50, message="Email length must be at most 50 characters")], render_kw={'placeholder': 'Enter Email...', 'class': 'email-input'})