"""
Custom Field for Website
"""
# ------------------ Imports ------------------
from wtforms import SubmitField
from ProjectsWebsite.forms.widget import ButtonWidget

# ------------------ Field ------------------
__all__ = ["ButtonField"]
class ButtonField(SubmitField):
    """
    Returns a button in the form.
    """
    widget = ButtonWidget()