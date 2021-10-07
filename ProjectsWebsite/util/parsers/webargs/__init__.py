"""
WebArgs Parser for parsing Nested url parameters
"""
# ------------------ Imports ------------------
import re
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Mapping,
    NoReturn,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

import marshmallow as ma
from webargs.flaskparser import FlaskParser

try:
    from ProjectsWebsite.util import temp_save
except ModuleNotFoundError:
    from .. import temp_save

__all__ = ["EditProfUrlParser"]

# ------------------ Parser ------------------
Request = TypeVar("Request")
ValidateArg = Union[None, Callable, Iterable[Callable]]
ArgMap = Union[
    ma.Schema,
    Mapping[str, ma.fields.Field],
    Callable[[Request], ma.Schema],
]
del ma


class EditProfUrlParser(FlaskParser):
    """
    Parses nested query args

    This parser handles both nested and normal query args.
    It expects nested levels delimited by a period
    and then deserialize the query args into a
    temp_save dict.

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
            'name': 'John%20Boone',
            actions: {
                'action': 'delete',
                'item_id': 9
            }
        }
    """

    def __init__(
        self,
        defaults: Optional[Dict[str, Type]] = None,
        location: Optional[str] = None,
        *,
        unknown: Optional[str] = "_default",
        error_handler: Optional[Callable[..., NoReturn]] = None,
        schema_class: Optional[Type] = None,
    ):
        self.defaults = defaults
        super().__init__(
            location=location,
            unknown=unknown,
            error_handler=error_handler,
            schema_class=schema_class,
        )

    def load_querystring(self, req, schema):
        return _structureddict(str(req.query_string, encoding="utf-8"), self.defaults)

    def use_args(
        self,
        argmap: ArgMap,
        defaults: Optional[Dict[str, Type]] = None,
        req: Optional[Request] = None,
        *,
        location: Optional[str] = None,
        unknown: Optional[str] = ...,
        as_kwargs: bool = False,
        validate: ValidateArg = None,
        error_status_code: Optional[int] = None,
        error_headers: Optional[Mapping[str, str]] = None,
    ) -> Callable[..., Callable]:
        if defaults:
            self.defaults = defaults
        return super().use_args(
            argmap=argmap,
            req=req,
            location=location,
            unknown=unknown,
            as_kwargs=as_kwargs,
            validate=validate,
            error_status_code=error_status_code,
            error_headers=error_headers,
        )

    def _update_args_kwargs(
        self,
        args: Tuple,
        kwargs: Dict[str, Any],
        parsed_args: temp_save,
        as_kwargs: bool,
    ) -> Dict[Dict, Mapping]:
        """Update args or kwargs with parsed_args depending on as_kwargs"""
        for k in self.defaults.keys():
            # even though _setdefaults for _structureddict sets the defaults value, some of those values may be removed by the main Parser
            # so this serves as a double check to make sure all values are in the temp_save dict
            if k not in parsed_args:
                parsed_args[k] = self.defaults[k]
        return super()._update_args_kwargs(args, kwargs, parsed_args, as_kwargs)


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
    match = string_base[index:]
    if match.count("&") >= 1:
        return True
    return False


def _setdefaults(dict_: temp_save, defaults: Union[Dict[str, Type], Type[None]]):
    if not defaults:
        return dict_
    for k, v in defaults.items():
        if dict_.get_without_pop(k):
            continue
        dict_[k] = v
    return dict_


def _structureddict(params_, defaults: Optional[Dict[str, Type]] = None):
    def _pair(dict_: temp_save, params: str):
        nested_or_not = re.match(r"([^.]+)\.([^=]+)", params)
        if nested_or_not is not None:
            if dict_.get_without_pop(nested_or_not.group(1)) is None:
                dict_[nested_or_not.group(1)] = temp_save()
                value = re.search(
                    r"({})([^&]+|$)".format(
                        f"{nested_or_not.group(1)}.{nested_or_not.group(2)}="
                    ),
                    params,
                ).group(2)
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
                _pair(dict_, params)
            else:
                value = re.search(
                    r"({})([^&+|$)".format(
                        f"{nested_or_not.group(1)}.{nested_or_not.group(2)}="
                    ),
                    params,
                ).group(2)
                is_int = re.fullmatch(r"[^a-zA-Z]+", value)
                if is_int:
                    value = int(value)
                dict_[nested_or_not.group(1)][nested_or_not.group(2)] = value
                replace_string = (
                    f"{nested_or_not.group(1)}.{nested_or_not.group(2)}={value}"
                )
                and_ = _check_and_or_false(params, nested_value=value)
                if and_:
                    params = params.replace(replace_string, "")
                else:
                    params = params.replace(
                        f"{nested_or_not.group(1)}.{nested_or_not.group(2)}={value}", ""
                    )
                _pair(dict_, params)
        elif params == "":
            return dict_
        param = re.search(r"([^=]+)\=([^\&]+|$)", params)
        value = param.group(2)
        is_int = re.fullmatch(r"[^a-zA-Z]+", value)
        if is_int:
            value = int(value)
        and_ = _check_and_or_false(params, param)
        dict_[param.group(1)] = value
        replace_string = f"{param.group(1)}={value}"
        if and_:
            params = params.replace(f"{param.group(1)}={value}&", "")
        else:
            params = params.replace(f"{param.group(1)}={value}", "")
        _pair(dict_, params)

    dict_ = temp_save()
    _pair(dict_, params_)
    dict_ = _setdefaults(dict_, defaults)
    return dict_
