# ------------------ Helper Util: Import ------------------
from typing import Union



alertMessageType = Union[str, int]

EMAILS = []

ALERTS = {
    'success' : 'alert-success',
    'error' : 'alert-danger',
    'warn': 'alert-warnings'
}

alert_dict = {
    'type': '',
    'message':''
}