footerMenu = "ADD:n|SELECT:s|DISELECT:d|INFO:SPACE|\
INSTALL:i|UNINSTALL:u|REMOVE:0|EXIT:q"
footerEdit = "EDT:SPACE|SAVE:s|VIEW:v|EXIT:q"
scriptMessage = """# Preset envvars:
#    $TMPDIR - temporary directory
#    $APPDIR - applications directory"""
populateMessage = """database is empty
to populate database with default entries
use --populate-db option"""


class bcolors(object):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
