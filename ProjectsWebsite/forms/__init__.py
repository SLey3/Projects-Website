"""
forms for MyProjects
"""
# ------------------ Imports ------------------
try:
    import ProjectsWebsite.forms.field
    import ProjectsWebsite.forms.validators
    from ProjectsWebsite.forms._forms import *
except ModuleNotFoundError:
    from ._forms import *
    from .field import *
    from .validators import *
