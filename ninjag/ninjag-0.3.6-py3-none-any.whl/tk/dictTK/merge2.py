"""
Merge two dictionaries into one.
"""
from typing import Dict
import copy


def merge2(dict1, dict2):
    # type: (Dict, Dict) -> Dict
    """Recrusively merge two dictionaries.

    The two input dictionaries can have arbitrary depths.
    If there is a conflict, values from dict2 will
    override dict1.

    Args:
        dict1 (dict): input dictionary 1
        dict2 (dict): input dictionary 2

    Returns:
        A new dictionary that combines both inputs.

    """
    ooo = copy.deepcopy(dict1)
    for k in dict2:
        if (k in dict1 and  # merge dictionaries
                isinstance(dict1[k], dict) and
                isinstance(dict2[k], dict)):
            ooo[k] = merge2(dict1[k], dict2[k])
        elif (k in dict1 and  # merge lists
                isinstance(dict1[k], list) and
                isinstance(dict2[k], list)):
            ooo[k] = dict1[k] + dict2[k]
        else:  # dict2 has priority (add new or override)
            ooo[k] = dict2[k]
    return ooo
