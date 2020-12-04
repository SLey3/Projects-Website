"""
Custom Field for Website
"""
# ------------------ Imports ------------------
from wtforms import StringField
from flask_wtf import FlaskForm
from .validators import (
    DataRequired, Email, Length
)

# ------------------ Field ------------------
class EmailField(FlaskForm):
    """
    Produces only the email field
    """
    email = StringField('email', validators=[DataRequired("Email Entry required"), Email("This must be an email", check_deliverability=True),
                                            Length(min=3, max=50, message="Email length must be at most 50 characters")], 
                        render_kw={"placeholder": "Enter Email"})