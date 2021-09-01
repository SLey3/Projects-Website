"""
WebArgs Parser for Nested url parameters
source: https://webargs.readthedocs.io/en/latest/advanced.html#custom-parsers
"""
import re
from functools import partialmethod
from typing import TypeVar

from webargs import core
from webargs.flaskparser import FlaskParser

from ProjectsWebsite.util import temp_save

__all__ = ["EditProfUrlParser"]

K = TypeVar("K")
V = TypeVar("V")


class EditProfUrlParser(FlaskParser):
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

    the URL query params `?name=John%20Boone&page=1`
    will yield the following dict:

        {
            'name': 'John Boone',
            'page': 1
        }

    the URL query params `?name=John%20Boone&actions.action=delete&actions.item_id=9`
    will yield the following dict:
        {
            'name': 'John Boone',
            actions: {
                'action': 'delete',
                'item_id': 9
            }
        }
    """

    def load_querystring(self, req, schema):
        print(type(req))
        print(req.args)
        print(req.query_string)
        return _structureddict(req.args)

    use_args = partialmethod(FlaskParser.use_args, location="query")


def _structureddict(dict_):
    # modified to use ProjectsWebsite.utils._utils.temp_save dictionary
    def _pair(r: temp_save, key: K, value: V):
        # modified to use ProjectsWebsite.utils._utils.temp_save dictionary
        print(r)
        m = re.match(r"(\w+)\.(.*)", key)
        if m:
            print(m.group(0))
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
    return r
