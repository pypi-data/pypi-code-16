import os
import nose2
import nose2
import unittest
import shutil
import yaml
from headjack.utKit import utKit

from fundamentals import tools


# SETUP AND TEARDOWN FIXTURE FUNCTIONS FOR THE ENTIRE MODULE
moduleDirectory = os.path.dirname(__file__)
utKit = utKit(moduleDirectory)
log, dbConn, pathToInputDir, pathToOutputDir = utKit.setupModule()
utKit.tearDownModule()


# load settings
settingsFile = pathToInputDir + "/example_settings.yaml"
# settingsFile = "/Users/Dave/.config/headjack/headjack.yaml"


stream = file(settingsFile, 'r')
settings = yaml.load(stream)
stream.close()


su = tools(
    arguments={"settingsFile": settingsFile},
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
# xt-setup-unit-testing-files-and-folders


class test_sendToKindle(unittest.TestCase):

    def test_pdf_list(self):
        from headjack.read import get_pdf_paths
        pdfDict = get_pdf_paths(
            log=log,
            settings=settings
        )

    def test_mobi_gen_function(self):

        from headjack.read import sendToKindle
        sender = sendToKindle(
            log=log,
            settings=settings,
            dbConn=dbConn
        )
        sender._trigger_docx_generation(pdfPath=pathToOutputDir + "test2.pdf")
        sender._trigger_docx_generation(pdfPath=pathToOutputDir + "test.pdf")

    # def test_web_sendToKindle_function(self):
    #     from headjack.read import sendToKindle
    #     sender = sendToKindle(
    #         log=log,
    #         settings=settings,
    #         dbConn=dbConn
    #     )
    #     sender.send_webarticles()

    # def test_pdf_sendToKindle_function(self):

    #     from headjack.read import sendToKindle
    #     sender = sendToKindle(
    #         log=log,
    #         settings=settings,
    #         dbConn=dbConn
    #     )
    #     sender.send_pdfs()

    def test_sendToKindle_function_exception(self):

        from headjack.read import sendToKindle
        try:
            this = sendToKindle(
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
