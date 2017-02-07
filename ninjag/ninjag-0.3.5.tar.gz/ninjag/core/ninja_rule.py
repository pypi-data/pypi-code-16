from .ninja_io import ninja_io


def ninja_rule(rules):
    """Return a list of Ninja rules

    Args:
        rules (list): a list of dictionaries of rules
    Returns:
        a list, each item is a string like
        rule <rule name>
            command = ...
    """
    output = []
    for d in rules:
        for k in sorted(d.keys()):
            v = d[k]
            if k in ['include', 'subninja']:
                output.append(
                    "{}: {}".format(k, ninja_io(v))
                    )
            else:
                output.append(
                    "rule {}\n  command = {}".format(k, v)
                )
    return "\n\n".join(output)
