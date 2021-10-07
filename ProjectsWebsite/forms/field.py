"""
Custom Field for Website
"""
# ------------------ Imports ------------------
from wtforms import SubmitField

try:
    from ProjectsWebsite.forms.widget import ButtonWidget
except ModuleNotFoundError:
    from .widget import ButtonWidget

# ------------------ Field ------------------
__all__ = ["ButtonField"]


class ButtonField(SubmitField):
    """
    Returns a button in the form.
    """

    widget = ButtonWidget()
