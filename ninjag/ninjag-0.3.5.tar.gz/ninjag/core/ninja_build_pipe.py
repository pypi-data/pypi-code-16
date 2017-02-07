import re


def ninja_build_pipe(config_dict, key):
    """Add Ninja build dependency or implicit output

    note: config_dict['dep'] can be a string or list
    Args:
        config_dict (dict): a specific
            configuration dictionary
        key (str): either 'out|', 'dep|' or 'dep||'
    Returns:
        an empty string if config_dict['dep']
        doesn't exist;
        returns " | dep1 dep2" if present
    """
    # extract "|" or "||" from key
    sep = re.sub(r"\w+", "", key)

    if key in config_dict:
        if isinstance(config_dict[key], str):
            return " {} {}".format(sep, config_dict[key])
        elif isinstance(config_dict[key], list):
            return " {} {}".format(
                sep,
                " ".join(map(str, config_dict[key]))
                )
        else:
            return ""
    else:
        return ""
