"""
WebArgs Parser for Nested url parameters
source: https://webargs.readthedocs.io/en/latest/advanced.html#custom-parsers
"""
from typing import TypeVar
from webargs import core
from webargs.flaskparser import FlaskParser
from ProjectsWebsite.util import temp_save
import re

__all__ = ["WebArgsNestedParser"]

K = TypeVar("K")
V = TypeVar("V")

class WebArgsNestedParser(FlaskParser):
    """
    Parses nested query args

    This parser handles nested query args. It expects nested levels
    delimited by a period and then deserializes the query args into a
    nested dict.

    For example, the URL query params `?name.first=John&name.last=Boone`
    will yield the following dict:

        {
            'name': {
                'first': 'John',
                'last': 'Boone',
            }
        }
    """
    def load_querystring(self, req, schema):
        return _structureddict(req.args)
    
def _structureddict(dict_):
    # modified to use ProjectsWebsite.utils._utils.temp_save dictionary
    def _pair(r: temp_save, key: K, value: V):
        # modified to use ProjectsWebsite.utils._utils.temp_save dictionary
        print(r)
        m = re.match(r"(\w+)\.", key)
        if m:
            print(m.group(1), "Group 2: ", m.group(2))
            if r.get_without_pop(m.group(1)) is None:
                r[m.group(1)] = temp_save()
                print(r.get_without_pop(m.group(1)))
            _pair(r.get_without_pop(m.group(1)), m.group(2), value)
        else:
            r[key] = value
            print("Current dict value with key: ", r.get_without_pop(key))
    r = temp_save()
    for k, v in dict_.items():
        print("Key: ", k, "Value: ", v)
        _pair(r, k, v)
    print(r.items())
    return r