# ------------------ Imports ------------------
from typing import List
from copy import deepcopy

# ------------------ Filter ------------------
def letterFilter(template: List[str]) -> list:
    """
    filters "escape newline" from the letter template
    """
    filter_character = ['\n']
    new_template = deepcopy(template)
    for char in new_template[:]:
        if char not in filter_character:
            if any([x in char for x in filter_character]):
                i = new_template.index(char)
                char = char.replace('\n', '')
                new_template[i] = char
        else:
            new_template.remove(char)
    return new_template
