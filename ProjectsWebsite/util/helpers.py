"""
Web helpers 
"""
# ------------------ Helper Util: Import ------------------
from typing import Union
import re

# ------------------ Helper Util ------------------

__all__ = [
    "alertMessageType",
    "email_re",
    "date_re",
    "bool_re",
    "InvalidType",
    "OperationError"
]

alertMessageType = Union[str, int]

email_re = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

date_re = re.compile(r'''[^a-zA-Z] # No word characters allowed
                         \d{1,2}/ # Month
                         \d{1,2}/ # Day
                         \d{2,4}  # Year''', re.X)

bool_re = re.compile(r'True|False')

class InvalidType(Exception):
    """
    Raised when theres an Invalid type
    """
    def __init__(self, msg):
        super().__init__(msg)
        
class OperationError(Exception):
    """
    Raised when a backend Operation goes wrong
    """
    def __init__(self, msg, exc_type):
        self.msg = msg
        self.exc_type = exc_type
        super().__init__(msg)
    def __str__(self):
        return "{exc} --> {msg}".format(exc=self.exc_type, msg=self.msg)