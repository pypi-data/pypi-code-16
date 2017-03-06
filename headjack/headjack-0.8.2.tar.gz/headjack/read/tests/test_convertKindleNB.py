import os
import nose2
import nose2
import unittest
import shutil
import yaml

from headjack.utKit import utKit

from fundamentals import tools


# # load settings
# stream = file(
#     "/Users/Dave/.config/headjack/headjack.yaml", 'r')
# settings = yaml.load(stream)
# stream.close()

# SETUP AND TEARDOWN FIXTURE FUNCTIONS FOR THE ENTIRE MODULE
moduleDirectory = os.path.dirname(__file__)
utKit = utKit(moduleDirectory)
log, dbConn, pathToInputDir, pathToOutputDir = utKit.setupModule()
utKit.tearDownModule()

# load settings
stream = file(
    pathToInputDir + "/example_settings.yaml", 'r')
settings = yaml.load(stream)
stream.close()

su = tools(
    arguments={"settingsFile": pathToInputDir + "/example_settings.yaml"},
    docString=__doc__,
    logLevel="DEBUG",
    options_first=False,
    projectName="headjack"
)
arguments, settings, log, dbConn = su.setup()

import shutil
try:
    shutil.rmtree(pathToOutputDir)
except:
    pass

# Recursively create missing directories
# if not os.path.exists(pathToOutputDir):
#     os.makedirs(pathToOutputDir)

shutil.copytree(pathToInputDir, pathToOutputDir)


class test_convertKindleNB(unittest.TestCase):

    def test_convertKindleNB_function(self):

        exists = os.path.exists(
            "/Users/Dave/git_repos/headjack/headjack/read/tests/output/reading-list")
        print exists

        from headjack.read import convertKindleNB
        this = convertKindleNB(
            log=log,
            settings=settings,
            dbConn=dbConn
        )
        this.convert()

    def test_convertKindleNB_function_exception(self):

        from headjack.read import convertKindleNB
        try:
            this = convertKindleNB(
                log=log,
                settings=settings,
                fakeKey="break the code"
            )
            this.get()
            assert False
        except Exception, e:
            assert True
            print str(e)

        # x-print-testpage-for-pessto-marshall-web-object

    # x-class-to-test-named-worker-function
