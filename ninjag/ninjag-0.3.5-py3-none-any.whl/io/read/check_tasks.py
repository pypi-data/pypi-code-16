from .check_types import check_types


def check_tasks(tasks):
    """Check tasks section"""
    if not isinstance(tasks, list):
        print("Error hint: \"tasks\" section must be a list")
        exit()

    for i, d in enumerate(tasks):
        for k in ["rule", "out"]:
            if k not in d:
                msg = "Error hint:  task[{}] ".format(i+1)
                msg += "is missing required field: \"{}\"".format(k)
                print(msg)
                exit()
            else:
                pass

        if "def" in d:
            check_types(d['def'], "task/def", [list, dict])
        else:
            pass

    return True
