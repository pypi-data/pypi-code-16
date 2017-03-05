import os,sys

from Utils import Utils
from exceptions import *


class KaptlStatus:
    def __init__(self):
        self.app_name = ""
        try:
            for filename in os.listdir(os.getcwd() + "/.kaptl"):
                if filename.endswith(".kaptl.old"):
                    self.app_name = filename[:-10]
        except WindowsError:
            print("Could not find a .kaptl file. Please check the current directory. Exiting... ")
            sys.exit(3)

        if self.app_name is "":
            raise NotKaptlProjectException("ERROR: Directory does not contain a KAPTL project")

        self.rules_old = Utils.read_rules_from_file(os.getcwd() + "/.kaptl/" + self.app_name + ".kaptl.old")\
            .splitlines()
        self.rules_new = Utils.read_rules_from_file(os.getcwd() + "/" + self.app_name + ".kaptl").splitlines()

    def display(self):
        if os.path.exists(os.getcwd() + "/.kaptl"):
            joined_diff = Utils.diff_two_strings(self.rules_old, self.rules_new)
            if joined_diff != '':
                print joined_diff
            else:
                print "KAPTL rules were not updated since the last build"

        else:
            raise NotKaptlProjectException("ERROR: Directory does not contain a KAPTL project")
