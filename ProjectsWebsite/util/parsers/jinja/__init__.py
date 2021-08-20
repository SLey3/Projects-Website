from typing import Union
from flask import current_app
from ProjectsWebsite.util.parsers.jinja.constants import *

class JinjaParser:
    """
    custom jinja parser to parse out js code for jinja syntax
    """
    def __init__(self, data: Union[str, list]):
        self.data = data
        self.env = current_app.jinja_env