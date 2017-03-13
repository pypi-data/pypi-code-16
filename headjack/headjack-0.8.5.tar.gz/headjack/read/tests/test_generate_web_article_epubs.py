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

# xt-setup-unit-testing-files-and-folders


class test_generate_web_article_epubs(unittest.TestCase):

    def test_generate_web_article_epubs_function(self):

        from headjack.read import generate_web_article_epubs
        this = generate_web_article_epubs(
            log=log,
            settings=settings,
            dbConn=dbConn
        )
        this.create()

    def test_generate_web_article_epubs_function_exception(self):

        from headjack.read import generate_web_article_epubs
        try:
            this = generate_web_article_epubs(
                log=log,
                settings=settings,
                fakeKey="break the code"
            )
            this.create()
            assert False
        except Exception, e:
            assert True
            print str(e)

        # x-print-testpage-for-pessto-marshall-web-object

    # x-class-to-test-named-worker-function
