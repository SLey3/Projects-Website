# ------------------ Imports ------------------
from copy import deepcopy
from typing import List

# ------------------ Filter ------------------
__all__ = ["letterFilter"]


def letterFilter(template: List[str]) -> List[str]:
    """
    filters "escape newline" from the letter template
    """
    filter_character = ["\n"]
    new_template = deepcopy(template)
    for char in new_template[:]:
        i = new_template.index(char)
        if char not in filter_character:
            if any([x in char for x in filter_character]):
                new_template[i] = char.strip()
            continue
        else:
            new_template.remove(char)
    return new_template
