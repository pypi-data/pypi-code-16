import os
import sys
import uuid
from Utils import Utils

from Common import Common
from KaptlClient import KaptlClient

from exceptions import *

class KaptlParse:
    def __init__(self, session, arguments):
        self.arguments = arguments
        self.session = session
        self.kaptl_client = KaptlClient(self.session, arguments)

        self.recipe = self.arguments["--recipe"]
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
        self.app_name = str(uuid.uuid4())
        self.angular_only = Utils.check_if_angular_only(self.stack)

    def parse(self):
        response = self.kaptl_client.send_parse_rules_request(
            self.rules,
            self.stack,
            recipe=self.recipe,
            recipe_version=self.recipe_version,
            return_compiler_output=True
        )
        response_content = response.json()
        if response.status_code and response_content["success"]:
            print "KAPTL build completed successfully."
        else:
            print "ERROR: KAPTL build error."
        output = response_content["compilerOutput"]
        output = output.replace('&nbsp;', ' ')
        print output
        sys.exit()

