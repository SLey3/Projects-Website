# ------------------ Imports ------------------
from marshmallow import Schema, fields

# ------------------ Schemas ------------------
__all__ = ["AccountUserManagementWebArgs"]


class _account_user_management_webargs_nested(Schema):
    """
    Nested parameters for the account user management page
    """

    action = fields.Str(load_default="None")
    item_id = fields.Str(load_default="None")


class AccountUserManagementWebArgs(Schema):
    """
    account user management schema
    """

    user = fields.Str(required=True)
    page = fields.Integer(load_default=1)
    actions = fields.Nested(_account_user_management_webargs_nested, many=True)
