"""
Web helpers 
"""
import re

# ------------------ Helper Util ------------------

__all__ = [
    "email_re",
    "date_re",
    "bool_re",
    "OperationError",
]

email_re = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

date_re = re.compile(
    r"""[^a-zA-Z] # No word characters allowed
                         \d{1,2}/ # Month
                         \d{1,2}/ # Day
                         \d{2,4}  # Year
                         """,
    re.X,
)

reversed_date_re = re.compile(
    r"""[^a-zA-z] # No word characters allowed
                                  \d{2,4}- # Year
                                  \d{1,2}- # Month
                                  \d{1,2} # year
                                  """,
    re.X,
)

bool_re = re.compile(r"True|False")


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
