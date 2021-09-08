"""
WebArgs Parser for Nested url parameters
source: https://webargs.readthedocs.io/en/latest/advanced.html#custom-parsers
"""
# ------------------ Imports ------------------
import re
from functools import partialmethod
from typing import Optional

from webargs.flaskparser import FlaskParser

from ProjectsWebsite.util import temp_save

__all__ = ["EditProfUrlParser"]

# ------------------ Parser ------------------


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
        return _structureddict(str(req.query_string, encoding="utf-8"))

    use_args = partialmethod(FlaskParser.use_args, location="query")


def _check_and_or_false(
    string_base: str,
    match_obj: Optional[re.Match] = None,
    nested_value: Optional[str] = None,
) -> bool:
    index = (
        string_base.index(match_obj.group(2))
        if not nested_value
        else string_base.index(nested_value)
    )
    print(index)
    match = string_base[index:]
    print(match)
    if string_base.count("&") >= 1:
        return True
    return False


def _structureddict(params_):
    # sys.setrecursionlimit(10 ** 6)
    def _pair(dict_: temp_save, params: str):
        print(params)
        nested_or_not = re.match(r"([^.]+)\.([^=]+)", params)
        print(type(nested_or_not))
        if nested_or_not is not None:
            print(nested_or_not.group(1))
            if dict_.get_without_pop(nested_or_not.group(1)) is None:
                dict_[nested_or_not.group(1)] = temp_save()
                value = re.search(
                    r"({})([^&]+|$)".format(
                        f"{nested_or_not.group(1)}.{nested_or_not.group(2)}="
                    ),
                    params,
                ).group(2)
                print(value)
                and_ = _check_and_or_false(params, nested_value=value)
                dict_[nested_or_not.group(1)][nested_or_not.group(2)] = value
                if and_:
                    params = params.replace(
                        f"{nested_or_not.group(1)}.{nested_or_not.group(2)}={value}&",
                        "",
                    )
                else:
                    params = params.replace(
                        f"{nested_or_not.group(1)}.{nested_or_not.group(2)}={value}", ""
                    )
                print(params)
                print(dict_)
                _pair(dict_, params)
            else:
                value = re.search(
                    r"({})([^&+|$)".format(
                        f"{nested_or_not.group(1)}.{nested_or_not.group(2)}="
                    ),
                    params,
                ).group(2)
                print(value)
                dict_[nested_or_not.group(1)][nested_or_not.group(2)] = value
                replace_string = (
                    f"{nested_or_not.group(1)}.{nested_or_not.group(2)}={value}"
                )
                if "&" in replace_string:
                    params = params.replace(replace_string, "")
                else:
                    params = params.replace(
                        f"{nested_or_not.group(1)}.{nested_or_not.group(2)}={value}", ""
                    )
                print(params)
                print(dict_)
                _pair(dict_, params)
        elif params == "":
            print("no more values for param")
            return dict_
        param = re.search(r"([^=]+)\=([^\&]+|$)", params)
        and_ = _check_and_or_false(params, param)
        print(and_)
        dict_[param.group(1)] = param.group(2)
        replace_string = f"{param.group(1)}={param.group(2)}"
        if and_:
            params = params.replace(f"{param.group(1)}={param.group(2)}&", "")
        else:
            params = params.replace(f"{param.group(1)}={param.group(2)}", "")
        print(params)
        print(dict_)
        _pair(dict_, params)

    print(len(params_))
    dict_ = temp_save()
    _pair(dict_, params_)
    return dict_
