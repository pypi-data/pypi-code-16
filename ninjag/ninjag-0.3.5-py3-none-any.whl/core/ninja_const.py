from .ninja_io import ninja_io


def ninja_const(defs, indent=""):
    """Return a list of user defined constants

    If the value of the const definition is a list,
    then it will be concatenated.

    Args:
        defs (list): a list of dictionaries of constant definitions
        indent (str): indentation for each definition

    Returns:
        a string
    """
    output = []
    for d in defs:
        for k in sorted(d.keys()):
            v = d[k]
            output.append(
                    "{}{} = {}".format(indent, k, ninja_io(v))
                )
    return "\n".join(output)
