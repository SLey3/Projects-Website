"""
widget for forms
"""
# ------------------ Import ------------------
try:
    from ProjectsWebsite.forms.widget._widget import *
    from ProjectsWebsite.forms.widget._widget import __all__ as __wall__
except ModuleNotFoundError:
    from ._widget import *
    from ._widget import __all__ as __wall__

__all__ = __wall__
del __wall__
