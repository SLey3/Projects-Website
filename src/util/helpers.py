# ------------------ Helper Util: Import ------------------
from typing import Union

# ------------------ Helper Util ------------------

alertMessageType = Union[str, int]

EMAILS = []

class InvalidType(ValueError):
    """
    Raised when theres an Invalid type
    """
    def __init__(self, *args):
        self.args = args
        super().__init__(*self.args)