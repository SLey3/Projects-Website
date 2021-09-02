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
        return _structureddict(req.query_string)

    use_args = partialmethod(FlaskParser.use_args, location="query")


def _structureddict(params_):
    nested_dict_created = False

    def _pair(r: temp_save, params: str):
        nonlocal nested_dict_created
        nested_or_not = re.search(r"([^.]+)\.([^=]+)", params)
        if nested_or_not is not None:
            if r.get_without_pop(nested_or_not.group(1)) is None:
                nested_dict_created = True
                r[nested_or_not.group(1)] = temp_save()
                param_value = params.replace(
                    f"{nested_or_not.group(1)}.{nested_or_not.group}=", ""
                )
                i = param_value.index("&")
                value = param_value[:i]
                r[nested_or_not.group(1)][nested_or_not.group(2)] = value
                params = params.replace(
                    f"{nested_or_not.group(1)}.{nested_or_not.group}={value}&", ""
                )
                _pair(r, params)

    r = temp_save()
    _pair(r)
    return r


# current regex: (\?|\&)([^=]+)\=([^&]+)*
