def check_definitions(defs, field):
    """check const/rules definitions
    """
    if not isinstance(defs, list):
        print("Error hint: \"{}\" section must be a list".format(field))
        print("Your \"{}\" section has type: {}".format(field, type(defs)))
        exit()
    else:
        pass

    for d in defs:
        if not isinstance(d, dict):
            msg = ""
            msg += "Error hint: each \"{}\" ".format(field)
            msg += "definition must be a \"dict\"\n"
            msg += "Error hint: your {} definition:\n".format(field)
            msg += "\t{}\nhas type: {}".format(d, type(d))
            print(msg)
            exit()
    return True
