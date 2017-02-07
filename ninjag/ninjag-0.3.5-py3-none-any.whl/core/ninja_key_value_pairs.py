def ninja_key_value_pairs(key, values):
    """Add include/subninja fields
    Args:
        key (str): such as "include", "subninja"
        values (list): a list of strings
    Returns:
        a string
    """
    if isinstance(values, list):
        return "\n\n".join(
                map(
                    lambda x: "{} {}".format(key, x),
                    values
                    )
            )
    else:
        return "{} {}".format(key, values)
