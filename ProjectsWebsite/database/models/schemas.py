# ------------------ Imports ------------------
import marshmallow as ma

# ------------------ Schemas ------------------
__all__ = ["AccountUserManagementWebArgs"]


class AccountUserManagementWebArgs(ma.Schema):
    """
    account user management schema
    """

    user = ma.fields.String(required=True)
    page = ma.fields.Integer(default=1)
