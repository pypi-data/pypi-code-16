from os import environ


def setEnv(tempfold, appfold):
    home = environ["HOME"]
    if tempfold[0] == '~':
        tempfold = tempfold.replace('~', home, 1)
    if appfold[0] == '~':
        appfold = appfold.replace('~', home, 1)
    environ.update({"TEMPFOLD": tempfold,
                    "APPFOLD": appfold})


def unsetEnv():
    environ.pop("TEMPFOLD")
    environ.pop("APPFOLD")
