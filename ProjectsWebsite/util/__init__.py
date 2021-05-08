"""
web utilities
"""
# ------------------ Imports ------------------
from ProjectsWebsite.util._util import *
from ProjectsWebsite.util._util import __all__ as __mainall__
import ProjectsWebsite.util.helpers
from ProjectsWebsite.util.helpers import __all__ as __helperall__
import ProjectsWebsite.util.utilmodule
from ProjectsWebsite.util.utilmodule import __all__ as __utilmoduleall__
from ProjectsWebsite.util.mail import __all__ as __mailall__

__all__ = [__mailall__, __helperall__, __utilmoduleall__, __mailall__]
del __mailall__
del __helperall__
del __utilmoduleall__
del __mainall__