"""
Custom Field for Website
"""
# ------------------ Imports ------------------
from wtforms import SubmitField
from ProjectsWebsite.forms.widget import ButtonWidget

# ------------------ Field ------------------
class ButtonField(SubmitField):
    """
    Returns a button in the form.
    """
    widget = ButtonWidget()