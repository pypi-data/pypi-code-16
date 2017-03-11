"""Usage:
    scriptcrypt
    scriptcrypt [--db <db>] [--appdir <appdir>]
    scriptcrypt [--editor <editor>] [--viewer <viewer>] [--shell <shell>]
    scriptcrypt [--populate-db] [--populate-bash] [--populate-zsh]
    scriptcrypt [--populate-all]
    scriptcrypt --license
    scriptcrypt --version
    scriptcrypt -h | --help

Options:
    --db <db>               Database location
    --appdir <app_dir>      Installation directory envvar
    --editor <editor>       Command line text editor
    --viewer <viewer>       Command line text pager
    --shell <shell>         Shell to run scripts
    --populate-db           Populate db with defaults
    --populate-bash         Add bash completion commands
    --populate-zsh          Add zsh completion commands (oh-my-zsh only)
    --populate-all          Populate db, bash and zsh
    --license               Print license
    --version               Version of program
    --help                  This message
"""

import docopt
import curses
from scriptcrypt.mcurses.interface import TUI
import scriptcrypt.version
import scriptcrypt.validation
from sys import exit
from subprocess import run
from os.path import dirname


def main():
    args = docopt.docopt(__doc__, version=scriptcrypt.version.version)
    if args["--license"]:
        run(["cat", dirname(__file__) + "/LICENSE"])
        exit()
    settings = scriptcrypt.validation.checkall(args)

    mytui = TUI("sqlite:///" + settings["db"])
    mytui.APPDIR = settings["appdir"]
    mytui.PAGER = settings["viewer"]
    mytui.EDITOR = settings["editor"]
    mytui.SHELL = settings["shell"]

    curses.wrapper(mytui.setup)
