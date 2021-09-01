import re
from pathlib import Path
from typing import Union

from flask import current_app

from ProjectsWebsite.util.parsers.jinja.constants import *


class JinjaParser:
    """
    custom jinja parser to parse out js code for jinja syntax
    """

    def __init__(self, data: Union[str, Path]):
        self.data = (
            data.open("r", encoding="utf-8").readlines()
            if isinstance(data, Path)
            else [line for line in data]
        )
        self.env = current_app.jinja_env

    def parse(self):
        try:
            request = self.env.globals["request"]
            info_forms = self.env.globals["info_forms"]
        except Exception as e:
            raise ValueError(
                "Make sure to set the required values of request or info_forms in the jinja global"
            ) from e
        else:
            jinja_globals = (
                request,
                info_forms,
            )
        for line in self.data:
            print(line)
            match = re.findall(r"{}.+{}".format(START_VAR_BLOCK, END_VAR_BLOCK), line)
            print(match)
            if match != []:
                for block in match:
                    print(block)
                    content = block.replace("{{", "").replace("}}", "")
                    print(content)
                    if "." in content:
                        before_dot = content.index(".")
                        after_dot = content.index(".") + 1
                        method = content[after_dot:]
                        content = content[:before_dot]
                        print(method)
                        print(content)
                    else:
                        raise ValueError(
                            "Cannot parse variables found in the document lines"
                        )
                    glob_index = jinja_globals.index(content)
                    func = jinja_globals[glob_index]
                    response = getattr(func, method)
                    block = re.sub(
                        r"{}.+{}".format(START_VAR_BLOCK, END_VAR_BLOCK),
                        r"{}".format(response),
                        block,
                    )
                    print(block)
                for parsed in match:
                    line = re.sub(
                        r"{}.+{}".format(START_VAR_BLOCK, END_VAR_BLOCK),
                        r"{}".replace(parsed),
                        line,
                    )
                    print(line)
        return self.data
