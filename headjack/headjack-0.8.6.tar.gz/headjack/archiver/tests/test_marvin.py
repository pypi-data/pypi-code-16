import os
import nose
import shutil
import yaml
import unittest
from headjack.utKit import utKit

from fundamentals import tools


# # load settings
stream = file(
    "/Users/Dave/.config/headjack/headjack.yaml", 'r')
settings = yaml.load(stream)
stream.close()

# SETUP AND TEARDOWN FIXTURE FUNCTIONS FOR THE ENTIRE MODULE
moduleDirectory = os.path.dirname(__file__)
utKit = utKit(moduleDirectory)
log, dbConn, pathToInputDir, pathToOutputDir = utKit.setupModule()
utKit.tearDownModule()

su = tools(
    arguments={"settingsFile": pathToInputDir + "/example_settings.yaml"},
    docString=__doc__,
    logLevel="DEBUG",
    options_first=False,
    projectName="headjack"
)
arguments, settings, log, dbConn = su.setup()

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


class test_marvin(unittest.TestCase):

    def test_marvin_function(self):

        from headjack.archiver import marvin
        ma = marvin(
            log=log,
            settings=settings,
            dbConn=dbConn
        )
        exractedDir = ma.import_database(
            pathToMarvinBackup=pathToOutputDir + "/marvin.m3backup")
        print exractedDir

        ma.upload_marvin_images_to_flickr(photoDir=exractedDir + "/photos")

    def test_marvin_assets_function(self):

        from headjack.archiver import marvin
        ma = marvin(
            log=log,
            settings=settings,
            dbConn=dbConn
        )
        ma.generate_marvin_webarticle_assets()

    def test_marvin_trash_function(self):

        from headjack.archiver import marvin
        ma = marvin(
            log=log,
            settings=settings,
            dbConn=dbConn
        )
        ma.trash_articles()

    def test_marvin_mmd_generation_function(self):

        from headjack.archiver import marvin
        ma = marvin(
            log=log,
            settings=settings,
            dbConn=dbConn
        )
        print ma._convert_annotations_to_mmd_content(webarticleId=1151, tags=["john-nash"])

    def test_marvin_function_exception(self):

        from headjack.archiver import marvin
        try:
            this = marvin(
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
