# ------------------ Imports ------------------
from marshmallow import Schema, fields

# ------------------ Schemas ------------------
__all__ = ["AccountUserManagementWebArgs"]


class AccountUserManagementWebArgs(Schema):
    """
    account user management schema
    """

    user = fields.String(required=True)
    page = fields.Integer(default=1)
