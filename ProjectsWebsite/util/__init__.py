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
from itertools import zip_longest

__all__ = []
for (func1, func2, func3, func4) in zip_longest(__mainall__, __helperall__, __utilmoduleall__, __mailall__, fillvalue=0):
    __all__.extend([func1, func2, func3, func4])
    
__all__ = list(dict.fromkeys(__all__))

del zip_longest
del __mailall__
del __helperall__
del __utilmoduleall__
del __mainall__