#! #!/usr/bin/python

import subprocess
import webbrowser
import platform
import os



if __name__ == "__main__":
    url = "http://localhost:8000"

    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    MANAGE = os.path.join(BASE_DIR,"Lib","site-packages","django_analysis_tool","manage.py")


    if platform.python_version().startswith("2.7"):
        subprocess.Popen(['python',MANAGE,'runserver'])
        webbrowser.open(url)
    else:
        raw_input("Error: python version isn't 2.7.*. \n Ctrl+C to quit!")
        
        
