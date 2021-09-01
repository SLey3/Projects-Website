# ------------------ Imports ------------------
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField
from wtforms.fields.html5 import TelField, SearchField
from ProjectsWebsite.modules import img_set
from ProjectsWebsite.forms.validators import *
from ProjectsWebsite.forms.field import ButtonField

# ------------------ Forms------------------
__all__ = [
    "loginForm",
    "registerForm",
    "articleForm",
    "contactForm",
    "forgotForm",
    "forgotRequestForm",
    "AccountManegementForms",
]


class loginForm(FlaskForm):
    """
    website login Form for loginpage.html
    """

    username = StringField(
        "username",
        validators=[
            InputRequired(message="Username field should not be blank"),
            Length(min=3, max=50, message="Email length must be at most 50 characters"),
            Email(message="This must be an Email", check_deliverability=True),
        ],
        render_kw={"autocomplete": "off"},
    )
    password = PasswordField(
        "password",
        validators=[
            InputRequired("Password field should not be blank"),
            Length(
                min=8, max=99, message="""length should be between 8-99 characters"""
            ),
        ],
    )


class registerForm(FlaskForm):
    """
    registration form for website
    """

    name = StringField(
        "name",
        validators=[
            DataRequired("Name Entry required"),
            Length(
                min=3, max=30, message="Name length must be between 3-30 characters"
            ),
        ],
        render_kw={"placeholder": "Name"},
    )
    email = StringField(
        "email",
        validators=[
            DataRequired("Email Entry required"),
            Email("This must be an email", check_deliverability=True),
            Length(min=3, max=50, message="Email length must be at most 50 characters"),
        ],
        render_kw={"placeholder": "Email"},
    )
    password = PasswordField(
        "password",
        id="password",
        validators=[
            DataRequired("Password field must not be blank"),
            Length(min=8, max=99, message="length should be between 8-99 characters"),
            ValidatePasswordStrength(),
        ],
        render_kw={"placeholder": "Password"},
    )
    confirm_pass = PasswordField(
        "confirm_pass",
        id="confirm_pass",
        validators=[
            DataRequired("You must confirm the password."),
            EqualTo(
                "password", "Confirmation password must equal to the created password"
            ),
        ],
        render_kw={"placeholder": "confirm_pass"},
    )
    recaptcha = RecaptchaField()


class articleForm(FlaskForm):
    """
    article form for website
    """

    title = StringField("title", render_kw={"placeholder": "Enter title"})

    author = StringField("author", render_kw={"placeholder": "Enter Authors name"})

    short_desc = StringField(
        "short_description", render_kw={"placeholder": "Enter Short Description"}
    )
    front_image = FileField(
        "front_img", id="front-image", validators=[FileAllowed(img_set, "Images only")]
    )


class contactForm(FlaskForm):
    """
    Contact Us form
    """

    first_name = StringField(
        "first_name",
        validators=[
            DataRequired("First name Entry required"),
            Length(min=3, max=9, message="Name length must be between 3-9 characters"),
        ],
        render_kw={"class": "form-control"},
    )

    last_name = StringField(
        "last_name",
        validators=[
            DataRequired("First name Entry required"),
            Length(
                min=2, max=19, message="Name length must be between 2-19 characters"
            ),
        ],
        render_kw={"class": "form-control"},
    )

    inquiry_selection = SelectField(
        "inquiry",
        choices=[
            ("General", "General Inquiry"),
            ("Security", "Security Inquiry"),
            ("Article", "Article Inquiry"),
            ("Other Inquiry", "Other"),
        ],
        validators=[DataRequired("Inquiry Choice Required")],
        render_kw={"class": "form-control"},
    )

    email = StringField(
        "email",
        validators=[
            DataRequired("Email Entry required"),
            Email("This must be an email", check_deliverability=True),
            Length(min=3, max=50, message="Email length must be at most 50 characters"),
        ],
        render_kw={"class": "form-control"},
    )

    mobile = TelField(
        "mobile_number",
        validators=[DataRequired("Mobile Field Required"), ValidatePhone()],
        render_kw={"class": "form-control"},
    )

    message = TextAreaField(
        "message",
        validators=[Length(min=50, message="Body must have minimum 50 characters")],
        render_kw={"cols": 30, "rows": 10, "class": "form-control"},
    )


class forgotForm(FlaskForm):
    """
    Password change form for forgot password
    """

    new_password = PasswordField(
        "password",
        id="password",
        validators=[
            DataRequired("Password field Entry required."),
            Length(min=8, max=99, message="length should be between 8-99 characters"),
            ValidatePasswordStrength(),
        ],
        render_kw={"placeholder": "New Password"},
    )

    confirm_new_password = PasswordField(
        "confirm_new_password",
        id="confirm_pass",
        validators=[
            DataRequired("Password Confirmation Required"),
            EqualTo("new_password", "Passwords do not match."),
        ],
        render_kw={"placeholder": "Confirm Password"},
    )


class forgotRequestForm(FlaskForm):
    """
    Creates the Initial Forgot Request Form
    """

    email = StringField(
        validators=[
            DataRequired("Email Entry required"),
            Email("This must be an email", check_deliverability=True),
            Length(min=3, max=50, message="Email length must be at most 50 characters"),
        ],
        render_kw={"placeholder": "Enter Email"},
    )

    submit = SubmitField(id="sbmt-btn", render_kw={"value": "Send"})

    back_button = ButtonField(
        "Back to Login", id="btn-redirect", render_kw={"href": "/"}
    )


class AccountManegementForms:
    """
    Forms for account Mangement Admin dashboard
    """

    class tableSearchForm(FlaskForm):
        """
        Creates Search Input
        """

        command = SearchField(
            id="table-search",
            render_kw={
                "class": "tbl-srch",
                "placeholder": "Search",
                "autocomplete": "off",
            },
        )

        command_sbmt = ButtonField(
            '<i class="fa fa-search" aria-hidden="true"></i>',
            id="article-srch-btn",
            render_kw={"class": "article-search-btn"},
        )

    class ArticleDeleteForms(FlaskForm):
        """
        Submit fields for deleting article starting with the delete all field
        """

        delete_all = SubmitField(
            id="article-delete-all-sbmt", render_kw={"class": "article-dlt-a-sbmt"}
        )

        delete_article = ButtonField(
            "<i class='fa fa-trash-o' aria-hidden='true'></i>",
            render_kw={"class": "inner-article-delete-btn"},
        )

    class roleForm(FlaskForm):
        """
        Submit Field that raises an alert before deleting all roles
        """

        delete_all = SubmitField(
            id="role-delete-all-sbmt",
            render_kw={"class": "role-delete-all-btn", "value": "delete all"},
        )

        add_role = StringField(
            id="add-role-input",
            validators=[DataRequired("Field cannot be empty"), ValidateRole()],
            render_kw={
                "class": "add-role-form-input",
                "placeholder": "Enter Role",
                "autocomplete": "off",
            },
        )

        add_role_sbmt = SubmitField(
            id="add-role-sbmt", render_kw={"class": "add-role-sbmt-btn", "value": "Add"}
        )

        class deleteRoleTableForms(FlaskForm):
            member_field = ButtonField(
                '<i class="fa fa-trash-o" aria-hidden="true"></i>',
                id="member-data-role-type-container",
                render_kw={"class": "inner-delete-btn", "data-role-type": "member"},
            )

            verified_field = ButtonField(
                '<i class="fa fa-trash-o" aria-hidden="true"></i>',
                id="verified-data-role-type-container",
                render_kw={"class": "inner-delete-btn", "data-role-type": "verified"},
            )

            unverified_field = ButtonField(
                '<i class="fa fa-trash-o" aria-hidden="true"></i>',
                id="unverified-data-role-type-container",
                render_kw={"class": "inner-delete-btn", "data-role-type": "unverified"},
            )

            editor_field = ButtonField(
                '<i class="fa fa-trash-o" aria-hidden="true"></i>',
                id="editor-data-role-type-container",
                render_kw={"class": "inner-delete-btn", "data-role-type": "editor"},
            )

    class extOptionForm(FlaskForm):
        """
        Includes: Blacklist and UnBlacklist Buttons
        """

        blacklist = SubmitField(
            id="blacklist-btn", render_kw={"class": "blacklist", "value": "Blacklist"}
        )

        unblacklist = SubmitField(
            id="unBlacklist-btn",
            render_kw={"class": "blacklist", "value": "Remove Blacklist"},
        )

        reason = StringField(
            id="reason-field",
            validators=[
                Length(
                    min=0,
                    max=100,
                    message="Blacklist Reason may not be over 100 characters.",
                ),
                Optional(),
            ],
            render_kw={
                "class": "blacklist-reason",
                "autocomplete": "off",
                "placeholder": "Enter Reason...",
            },
        )

    class adminUserInfoForm(FlaskForm):
        """
        Creates Info Ediit form Inputs
        """

        name = StringField(
            "Name: ",
            id="edit-name-input",
            validators=[
                DataRequired("Name Entry required"),
                Length(
                    min=3, max=30, message="Name length must be between 3-30 characters"
                ),
            ],
            render_kw={
                "placeholder": "Edit name...",
                "class": "name-input",
                "autocomplete": "off",
            },
        )

        name_sbmt = SubmitField(
            id="name-sbmt-btn", render_kw={"value": "Submit", "class": "name-sbmt-btn"}
        )

        email = StringField(
            "Email: ",
            id="edit-email-input",
            validators=[
                DataRequired("Field may not be blank"),
                Email("This must be an email", check_deliverability=True),
                Length(
                    min=3, max=50, message="Email length must be at most 50 characters"
                ),
            ],
            render_kw={
                "placeholder": "Edit email...",
                "class": "email-input",
                "autocomplete": "off",
            },
        )

        email_sbmt = SubmitField(
            id="email-sbmt-btn",
            render_kw={"value": "Submit", "class": "email-sbmt-btn"},
        )

        password = PasswordField(
            "Password: ",
            id="edit-pwd-input",
            validators=[
                DataRequired("Field may not be blank"),
                Length(
                    min=8, max=99, message="length should be between 8-99 characters"
                ),
            ],
            render_kw={
                "placeholder": "Edit password...",
                "class": "pwd-input",
                "autocomplete": "off",
            },
        )

        password_sbmt = SubmitField(
            id="pwd-sbmt-btn", render_kw={"value": "Submit", "class": "pwd-sbmt-btn"}
        )

        active = StringField(
            "Active Status: ",
            id="edit-active-input",
            validators=[DataRequired("Field may not be blank"), ValidateBool()],
            render_kw={
                "placeholder": "Edit active status...",
                "class": "active-status-input",
                "autocomplete": "off",
            },
        )

        active_sbmt = SubmitField(
            id="active-status-sbmt-btn",
            render_kw={"value": "Submit", "class": "active-status-sbmt-btn"},
        )
