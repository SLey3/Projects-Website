# ------------------ Import ------------------
from itertools import zip_longest

try:
    import ProjectsWebsite.util.mail.filter
    from ProjectsWebsite.util.mail._mail import *
    from ProjectsWebsite.util.mail._mail import __all__ as __mainmailall__
    from ProjectsWebsite.util.mail.filter import __all__ as __filterall__
except ModuleNotFoundError:
    from ._mail import *
    from ._mail import __all__ as __mainmailall__
    from .filter import __all__ as __filterall__
    from .filter import letterFilter

__all__ = []

for (func1, func2) in zip_longest(__mainmailall__, __filterall__, fillvalue=0):
    __all__.extend([func1, func2])

del zip_longest
del __mainmailall__
del __filterall__
