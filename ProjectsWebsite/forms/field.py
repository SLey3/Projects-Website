"""
Custom Field for Website
"""
# ------------------ Imports ------------------
from wtforms import StringField
from forms.widget import ButtonWidget

# ------------------ Field ------------------
class ButtonField(StringField):
    """
    Returns a button in the form.
    """
    widget = ButtonWidget()