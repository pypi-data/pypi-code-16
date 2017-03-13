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

# Recursively create missing directories
# if not os.path.exists(pathToOutputDir):
#     os.makedirs(pathToOutputDir)

shutil.copytree(pathToInputDir, pathToOutputDir)

# xt-setup-unit-testing-files-and-folders


class test_docs(unittest.TestCase):

    def test_docs_function(self):

        from headjack.archiver import docs
        this = docs(
            log=log,
            settings=settings,
            dbConn=dbConn
        )
        this.stash()

        from headjack.archiver import docs
        this = docs(
            log=log,
            settings=settings,
            dbConn=dbConn
        )
        this.archive()

    # def test_parser_function(self):

    #     from headjack.archiver import docs
    #     this = docs(
    #         log=log,
    #         settings=settings,
    #         dbConn=dbConn
    #     )
    #     docMetadata = this.parse_associated_notes_file(
    #         markdownFilepath=pathToOutputDir + "Wave_particle_duality_-_Wikipedia_xx1577xx.md"
    #     )
    #     print docMetadata

    # def test_collection_function(self):

    #     from headjack.archiver import docs
    #     this = docs(
    #         log=log,
    #         settings=settings,
    #         dbConn=dbConn
    #     )
    #     docs, meta, mdNotes, mdContent = this._collect_docs_with_metadata(
    #         mediaStagingFolder=pathToOutputDir
    #     )
    #     print docs, meta, mdNotes

    def test_docs_function_exception(self):

        from headjack.archiver import docs
        try:
            this = docs(
                log=log,
                settings=settings,
                fakeKey="break the code"
            )
            this.archive()
            assert False
        except Exception, e:
            assert True
            print str(e)

        # x-print-testpage-for-pessto-marshall-web-object

    # x-class-to-test-named-worker-function
