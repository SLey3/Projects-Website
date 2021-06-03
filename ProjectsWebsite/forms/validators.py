# ------------------ Imports ------------------
from wtforms import ValidationError
from wtforms.validators import (
    InputRequired, Length,
    Email, DataRequired,
    EqualTo, Optional
)
from flask_wtf.file import FileField, FileAllowed
from typing import Optional as optional
from ProjectsWebsite.util.helpers import bool_re
from password_strength import PasswordPolicy
from password_strength.tests import NonLetters, Numbers, Special, Uppercase
import phonenumbers

# ------------------ Validators ------------------
__all__ = [
    "InputRequired", 
    "Length",
    "Email",
    "DataRequired",
    "EqualTo", 
    "Optional",
    "FileField",
    "FileAllowed",
    "ValidatePhone",
    "ValidateBool",
    "ValidateRole",
    "ValidatePasswordStrength"
]

def ValidatePhone(message: optional[str] = None):
    """
    validates phone number
    """
    if isinstance(message, type(None)):
        message = "Invalid Phone Number"
    else:
        message = message
    
    def _validatephone(form, field):
        if len(field.data) > 15:
            raise ValidationError("Invalid Phone Number")
        
        try:
            mobile_number = phonenumbers.parse(field.data)
            if not (phonenumbers.is_valid_number(mobile_number)):
                raise ValidationError(message)
        except:
            mobile_number = phonenumbers.parse("+1"+field.data)
            if not (phonenumbers.is_valid_number(mobile_number)):
                raise ValidationError(message)
    return _validatephone

def ValidateBool(python_bool: bool = True):
    """
    validates bool format
    """
    python_bool = python_bool
    def _validatebool(form, field):
        if len(field.data) < 4 and len(field.data) > 5:
            raise ValidationError("Field may not be less than 4 character and no more than 5 characters.")
        if python_bool:
            if not bool_re.match(field.data):
                raise ValidationError("Input is not in Python bool format or is not a bool.")
        else:
            import re
            other_bool_re = re.compile(r"True|False", re.I)
            if not other_bool_re.match(field.data):
                raise ValidationError("Input is not a bool.")
    return _validatebool


def ValidateRole():
    """
    validates role
    """
    def _validaterole(form, field):
        if len(field.data) >= 11:
            raise ValidationError("Length of Role may not be 12+ characters long")
        from ProjectsWebsite.database.models import Role
        if Role.is_role(field.data):
            pass
        else:
            raise ValidationError(f"{field.data} is not a valid role.")
    return _validaterole       

def ValidatePasswordStrength():
    """
    Checks Password Strength
    """
    failed_tests = []
    def _validateStrength(form, field):
        nonlocal failed_tests
        policy = PasswordPolicy.from_names(
            uppercase=3,
            numbers=4,
            special=2,
            nonletters=2)
        result = policy.test(field.data)
        if result == []:
            return None
        for test in result:
            if isinstance(test, Uppercase):
                failed_tests.append("uppercase letters")
            elif isinstance(test, Numbers):
                failed_tests.append("numbers")
            elif isinstance(test, Special):
                failed_tests.append("special characters")
            elif isinstance(test, NonLetters):
                failed_tests.append("non-letter characters")
        err = "The Password has less than the required limit(s) of: "
        for test in failed_tests:
            err +=  f'\n{test}'
        err += "."
        raise ValidationError(err)
    return _validateStrength