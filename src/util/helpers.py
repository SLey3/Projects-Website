"""
Web helpers 
"""
# ------------------ Helper Util: Import ------------------
from typing import Union
import re

# ------------------ Helper Util ------------------

alertMessageType = Union[str, int]

EMAILS = []

email_re = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

bool_re = re.compile(r'True|False')

class InvalidType(ValueError):
    """
    Raised when theres an Invalid type
    """
    def __init__(self, *args):
        self.args = args
        super().__init__(*self.args)