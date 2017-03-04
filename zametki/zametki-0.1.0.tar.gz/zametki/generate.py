import os
from os import path

import shutil

def generate(selectedpath):

   rootPath = path.split(path.abspath(__file__))[0]
   templatePath = path.join(rootPath, "zametki-template")
   
   try:
       yourpath = os.path.join(selectedpath, "./yourzametki")
       shutil.copytree(templatePath, yourpath)
       print ("Your Zametki folder is generated")
   except Exception:
       print ("Sorry your already have a zametki there")