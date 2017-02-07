from .check_tasks import check_tasks
from .check_types import check_types
from .assert_any import assert_any


def check_input(argd):
    """Check whether the user input is valid

    Args:
        argd (dict): user input dict
    Returns:
        same as input if no errors found
        otherwise exit with a message.
    """
    # check whether the required fields exist
    required = []
    for k in required:
        if k not in argd:
            print(
                "Error hint: missing required field: \"{}\"".format(k))
            exit()
        else:
            pass

    # check whether the formats are correct
    check_tasks(argd['task'])

    for key in ['def', 'rule', 'phony']:
        assert_any([check_types(argd[key], key, [list, dict])])

    for key in ['include', 'subninja', 'default']:
        assert_any(
                [
                    check_types(argd[key], key, [str]),
                    check_types(argd[key], key, [list, str])
                ]
            )

    return argd
