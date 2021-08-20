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

class ValidatePhone(object):
    """
    validates phone number
    """
    def __init__(self, message: optional[str] = None):
        if isinstance(message, type(None)):
            self.message = "Invalid Phone Number"
        else:
            self.message = message
        
    def __call__(self, form, field):
        if len(field.data) > 15:
            raise ValidationError("Invalid Phone Number Length")
        try:
            mobile_number = phonenumbers.parse(field.data)
            if not (phonenumbers.is_valid_number(mobile_number)):
                raise ValidationError(self.message)
        except:
            mobile_number = phonenumbers.parse("+1"+field.data)
            if not (phonenumbers.is_valid_number(mobile_number)):
                raise ValidationError(self.message)

class ValidateBool(object):
    """
    validates bool format
    """
    def __init__(self, python_bool: bool = True):
        self.python_bool = python_bool
    
    def __call__(self, form, field):
        if len(field.data) < 4 and len(field.data) > 5:
            raise ValidationError("Field may not be less than 4 character and no more than 5 characters.")
        if self.python_bool:
            if not bool_re.match(field.data):
                raise ValidationError("Input is not in Python bool format or is not a bool.")
        else:
            import re
            other_bool_re = re.compile(r"True|False", re.I)
            if not other_bool_re.match(field.data):
                raise ValidationError("Input is not a bool.")
            
class ValidateRole(object):
    """
    validates role
    """
    def __call__(self, form, field):
        if len(field.data) >= 11:
            raise ValidationError("Length of Role may not be 12+ characters long")
        from ProjectsWebsite.database.models import Role
        if Role.is_role(field.data):
            pass
        else:
            raise ValidationError(f"{field.data} is not a valid role.")
        
class ValidatePasswordStrength(object):
    """
    Checks Password Strength
    """   
    failed_tests = []
    
    def __call__(self, form, field):
        policy = PasswordPolicy.from_names(
        uppercase=2,
        numbers=4,
        special=2,
        nonletters=2)
        result = policy.test(field.data)
        if result == []:
            return None
        for test in result:
            if isinstance(test, Uppercase) and not isinstance(test, (Numbers, Special, NonLetters)):
                print("test is the instance of Uppercase")
                self.failed_tests.append(f"uppercase letters (Missing: {test.count})")
            elif isinstance(test, Numbers) and not isinstance(test, (Special, NonLetters)):
                self.failed_tests.append(f"numbers (Missing: {test.count})")
            elif isinstance(test, Special) and not isinstance(test, (Numbers, NonLetters)):
                print("test is the instance of Special")
                self.failed_tests.append(f"special characters (Missing: {test.count})")
            elif isinstance(test, NonLetters) and not isinstance(test, (Numbers, Special)):
                self.failed_tests.append(f"non-letter characters  (Missing: {test.count})")
        err = "The Password has less than the required limit(s) of: "
        for test in self.failed_tests:
            print(test)
            err +=  f'\n- {test}'
        err += "."
        raise ValidationError(err)
