# ------------------ Import ------------------
from enum import Enum


# ------------------ Roles Enum ------------------
class Roles(Enum):
    MEMBER = "<member>"
    EDITOR = "<editor>"
    VERIFIED = "<verified>"
    UNVERIFIED = "<unverified>"
    ADMIN = "<admin>"
