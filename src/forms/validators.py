# ------------------ Imports ------------------
from wtforms import ValidationError
from wtforms.validators import (
    InputRequired, Length,
    Email, DataRequired,
    EqualTo
)
from flask_wtf.file import FileField, FileAllowed
from typing import Optional
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