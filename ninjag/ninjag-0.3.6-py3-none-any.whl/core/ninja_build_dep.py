import re


def ninja_build_dep(task, key):
    """Add Ninja build dependency

    note: task['dep'] can be a string or list
    Args:
        task (dict): a specific task
        key (str): either 'dep|' or 'dep||'
        sep (str): the separator, either "|" or "||"
            "|" means implicit dependency
            "||" means order-only dependency
            (ninja-build.org/manual.html#ref_dependencies)
    Returns:
        an empty string if task['dep']
        doesn't exist;
        returns " | dep1 dep2" if present
    """
    # extract "|" or "||" from key
    sep = re.sub(r"\w+", "", key)

    if key in task:
        if isinstance(task[key], str):
            return " {} {}".format(sep, task[key])
        elif isinstance(task[key], list):
            return " {} {}".format(
                sep,
                " ".join(map(str, task[key]))
                )
        else:
            return ""
    else:
        return ""
