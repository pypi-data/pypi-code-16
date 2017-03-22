import os
import nose
import shutil
import unittest
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

try:
    shutil.rmtree(pathToOutputDir)
    # Recursively create missing directories
    shutil.copytree(pathToInputDir, pathToOutputDir)
except:
    pass


class test_papers(unittest.TestCase):

    def test_papers_function(self):

        from headjack.archiver import papers as p
        papers = p(
            log=log,
            settings=settings
        )
        papers.archive(pdfPath=pathToOutputDir +
                       "/st-devonthink/web-articles/Volkswagen - Wikipedia/Volkswagen - Wikipedia.pdf", delete=True)

    def test_papers_function_exception(self):

        from headjack.archiver import papers as p
        try:
            this = papers(
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
