import os
import nose
import shutil
import yaml
from tastic.utKit import utKit

from fundamentals import tools

su = tools(
    arguments={"settingsFile": None},
    docString=__doc__,
    logLevel="DEBUG",
    options_first=False,
    projectName="tastic"
)
arguments, settings, log, dbConn = su.setup()

# # load settings
# stream = file(
#     "/Users/Dave/.config/tastic/tastic.yaml", 'r')
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
workspaceRoot = pathToOutputDir + "/astronotes-wiki"
syncFolder = pathToOutputDir + "/astronotes-synctasks"


class test_sync_function_class(unittest.TestCase):

    def test_sync_function(self):

        from tastic.workspace import sync
        tp = sync(
            log=log,
            settings=settings,
            workspaceRoot=workspaceRoot,
            workspaceName="astronotes",
            syncFolder=syncFolder
        )
        tp.sync()

    def test_sync_function2(self):

        from tastic.workspace import sync
        tp = sync(
            log=log,
            settings=settings,
            workspaceRoot=workspaceRoot,
            workspaceName="astronotes",
            syncFolder=syncFolder,
            editorialRootPath=pathToOutputDir
        )
        tp.sync()

    # def test_two_way_sync_function(self):

    #     from tastic.workspace import sync
    #     tp = sync(
    #         log=log,
    #         settings=settings,
    #         workspaceRoot=workspaceRoot,
    #         workspaceName="astronotes",
    #         syncFolder=syncFolder
    #     )
    #     tp._complete_original_tasks()

    def test_sync_function_exception(self):

        from tastic.workspace import sync
        try:
            this = sync(
                log=log,
                settings=settings,
                fakeKey="break the code",
                workspaceRoot=workspaceRoot,
                syncFolder=syncFolder
            )
            this.get()
            assert False
        except Exception, e:
            assert True
            print str(e)

        # x-print-testpage-for-pessto-marshall-web-object

    # x-class-to-test-named-worker-function
