# ------------------ Imports ------------------
from wtforms import ValidationError
from wtforms.validators import (
    InputRequired, Length,
    Email, DataRequired,
    EqualTo
)
from flask_wtf.file import FileField, FileAllowed
from typing import Optional
from ProjectsWebsite.util.helpers import bool_re, date_re
import phonenumbers

# ------------------ Validators ------------------
def ValidatePhone(message: Optional[str] = None):
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