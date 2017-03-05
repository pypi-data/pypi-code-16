import os
import sys
import uuid
from Utils import Utils

from Common import Common
from KaptlClient import KaptlClient
from exceptions import *

class KaptlVersions:
    def __init__(self, session, arguments):
        self.arguments = arguments
        self.session = session
        self.common_methods = Common(self.session)
        arguments["--license"] = Utils.manifest("license") if not arguments["--license"] else arguments["--license"]
        self.kaptl_client = KaptlClient(session, arguments)

        self.recipe = self.arguments["--recipe"]

    def versions(self):
        versions = self.kaptl_client.get_versions(
            recipe=self.recipe
        )

        print "Available versions for '" + self.recipe + "' recipe:"
        for version in versions:
            print version
        sys.exit()