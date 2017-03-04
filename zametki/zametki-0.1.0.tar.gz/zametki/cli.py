"""
Zametki

Note that some commands can only be used in a zametki project folder

Usage:
    zametki generate <path>
    zametki generate-post <postname>
    zametki runserver
    zametki posts
    zametki readpost <postId>
    
Options:
    -h --help   Show this screen
    --version   Show version

Help:
    For help using this tool please open an issue on the Github repository:
    https://github.com/Mechasparrow/zametki

"""

from docopt import docopt

from zametki.generate import generate
import zametki.zametkiproject as zametkiproject

import os 
from os import path

def main():

    #Get the path to the zametki.project file
    zametki_project_path = path.join(os.getcwd(), "zametki.project")

    #Set the fact that it is a zametki project to True by default
    zametki_project = True

    try: 
        os.stat(zametki_project_path)
    except Exception:
        zametki_project = False

    """Main CLI entrypoint. """
    arguments = docopt(__doc__, version = "Zametki 0.1.0")
    print (arguments)
    if (arguments["generate"] == True):
        print ("will generate at path designated")
        generate(arguments["<path>"])
    elif (zametki_project == True):
        zametkiproject.main(arguments)
    else:
        print ("If the command does not work, please check that you are in the project directory")
    
    


