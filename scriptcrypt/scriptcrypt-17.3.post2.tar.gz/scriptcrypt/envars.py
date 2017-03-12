from os import environ


def setEnv(tempfold, appfold):
    home = environ["HOME"]
    if tempfold[0] == '~':
        tempfold = tempfold.replace('~', home, 1)
    if appfold[0] == '~':
        appfold = appfold.replace('~', home, 1)
    environ.update({"TMPDIR": tempfold,
                    "APPDIR": appfold})


def unsetEnv():
    environ.pop("TMPDIR")
    environ.pop("APPDIR")
