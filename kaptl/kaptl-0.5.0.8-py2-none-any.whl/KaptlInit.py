import sys

from Utils import Utils

from Common import Common
from exceptions import *
from KaptlClient import KaptlClient

class KaptlInit:
    def __init__(self, session, arguments):
        self.arguments = arguments
        self.app_name = self.arguments["<name>"]
        self.kaptl_client = KaptlClient(session, arguments)
        self.recipe = self.arguments["--recipe"]
        self.mode = self.arguments["--mode"]

        self.recipe_version = ""
        if self.arguments["--recipe-version"]:
            self.recipe_version = self.arguments["--recipe-version"]

        if self.arguments["<rules>"]:
            self.rules = self.arguments["<rules>"]
        elif self.arguments["--rules-file"]:
            self.rules = Utils.read_rules_from_file(self.arguments["--rules-file"])
        else:
            print "ERROR: Cannot find rules to use for creating a project. Aborting..."
            sys.exit(3)

        self.file_info = None

        self.stack = {}
        try:
            self.stack = Utils.get_stack_info(self.arguments)
        except WrongStackInfoException, e:
            print e.message
            sys.exit()

        self.angular_only = Utils.check_if_angular_only(self.stack)

    def initialize_project(self):
        self.session_name = self.kaptl_client.parse_rules(self.rules, self.stack, self.recipe, self.app_name, recipe_version=self.recipe_version)
        if self.session_name is not None:
            self.file_info = self.kaptl_client.get_file_info(self.session_name, self.rules, self.stack, self.recipe, mode="full", angular_only=self.angular_only, app_name=self.app_name)
            if self.file_info is not None:
                self.kaptl_client.download_file(self.file_info)
                Common.unzip_archive(self.file_info[1], existing=False)
            else:
                print "ERROR: Couldn't retrieve a file from the server. Try again later."
                sys.exit()
        else:
            # just exit, parse_rules will print the info about what happened
            sys.exit()
