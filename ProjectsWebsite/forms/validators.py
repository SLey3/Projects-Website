# ------------------ Imports ------------------
from typing import Optional as optional

import phonenumbers
from flask_wtf.file import FileAllowed, FileField
from wtforms import ValidationError
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    InputRequired,
    Length,
    Optional,
)

from ProjectsWebsite.util import NonDuplicateList, PasswordTestManager
from ProjectsWebsite.util.helpers import bool_re

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
    "ValidatePasswordStrength",
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
            mobile_number = phonenumbers.parse("+1" + field.data)
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
            raise ValidationError(
                "Field may not be less than 4 character and no more than 5 characters."
            )
        if self.python_bool:
            if not bool_re.match(field.data):
                raise ValidationError(
                    "Input is not in Python bool format or is not a bool."
                )
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

    failed_tests = NonDuplicateList()

    def __call__(self, form, field):
        policy = PasswordTestManager.from_names(uppercase=2, numbers=4, special=2)
        result = policy.test(field.data)
        if result == []:
            return
        for test in result:
            if test.is_uppercase:
                count = policy.find_missing_upper_characters(test)
                self.failed_tests.append(f"uppercase letters (Missing: {count})")
            elif test.is_numbers:
                count = policy.find_missing_number_characters(test)
                self.failed_tests.append(f"numbers (Missing: {count})")
            elif test.is_special:
                count = policy.find_missing_special_characters(test)
                self.failed_tests.append(f"special characters (Missing: {count})")
        err = "The Password has less than the required limit(s) of: "
        for test in self.failed_tests:
            err += f"\n- {test}"
        err += "."
        self.failed_tests.clean_similar(self.failed_tests.base_list)
        raise ValidationError(err)
