import os
import nose2
import nose2
import unittest
import shutil
import yaml
from headjack.utKit import utKit

from fundamentals import tools

su = tools(
    arguments={"settingsFile": None},
    docString=__doc__,
    logLevel="DEBUG",
    options_first=False,
    projectName="headjack"
)
arguments, settings, log, dbConn = su.setup()

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

import shutil
try:
    shutil.rmtree(pathToOutputDir)
except:
    pass
# COPY INPUT TO OUTPUT DIR
shutil.copytree(pathToInputDir, pathToOutputDir)

# Recursively create missing directories
if not os.path.exists(pathToOutputDir):
    os.makedirs(pathToOutputDir)

importFolder = pathToOutputDir + "/st-devonthink"
pathToDevonthinkDB = "/Users/Dave/Dropbox/devonthink/home media.dtBase2"
# xt-setup-unit-testing-files-and-folders


class test_devonthink(unittest.TestCase):

    def test_devonthink_function(self):

        from headjack.archiver import devonthink
        this = devonthink(
            log=log,
            settings=settings,
            importFolder=importFolder,
            pathToDevonthinkDB=pathToDevonthinkDB
        )
        this.ingest()

    def test_devonthink_function_exception(self):

        from headjack.archiver import devonthink
        try:
            this = devonthink(
                log=log,
                settings=settings,
                fakeKey="break the code"
            )
            this.ingest()
            assert False
        except Exception, e:
            assert True
            print str(e)

        # x-print-testpage-for-pessto-marshall-web-object

    # x-class-to-test-named-worker-function
