#!/usr/local/bin/python
# encoding: utf-8
"""
Documentation for headjack can be found here: http://headjack.readthedocs.org/en/stable

Usage:
    headjack read sendToKindle [-s <pathToSettingsFile>]
    headjack read convert kindleAnnotations [-s <pathToSettingsFile>]
    headjack web2epub [-s <pathToSettingsFile>]
    headjack media (stage|archive) [-s <pathToSettingsFile>]
    headjack marvin import [-s <pathToSettingsFile>]
    headjack marvin export [-s <pathToSettingsFile>]
    headjack dt <pathToImportFolder> <pathToDevonthinkDB> [-s <pathToSettingsFile>]

    marvin                convert and import the database exported from the Marvin iOS app, then export all read articles ready for import into devonthink
    web2epub              convert web-articles queued in the headjack database into epub books
    dt                    import a media package into devonthink

    pathToImportFolder    path to the root directory containing the package to import into a devonthink database
    pathToDevonthinkDB    path to the devonthink database to import the contain into
    
    -h, --help            show this help message
    -s, --settings        the settings file
"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
import readline
import glob
import pickle
from docopt import docopt
from fundamentals import tools, times
from datetime import datetime, date, time

# from ..__init__ import *


def tab_complete(text, state):
    return (glob.glob(text + '*') + [None])[state]


def main(arguments=None):
    """
    *The main function used when ``cl_utils.py`` is run as a single script from the cl, or when installed as a cl command*
    """
    # setup the command-line util settings
    su = tools(
        arguments=arguments,
        docString=__doc__,
        logLevel="DEBUG",
        options_first=False,
        projectName="headjack"
    )
    arguments, settings, log, dbConn = su.setup()

    # tab completion for raw_input
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(tab_complete)

    # unpack remaining cl arguments using `exec` to setup the variable names
    # automatically
    for arg, val in arguments.iteritems():
        if arg[0] == "-":
            varname = arg.replace("-", "") + "Flag"
        else:
            varname = arg.replace("<", "").replace(">", "")
        if isinstance(val, str) or isinstance(val, unicode):
            exec(varname + " = '%s'" % (val,))
        else:
            if varname == "import":
                varname = "iimport"
            exec(varname + " = %s" % (val,))
        if arg == "--dbConn":
            dbConn = val
        log.debug('%s = %s' % (varname, val,))

    ## START LOGGING ##
    startTime = times.get_now_sql_datetime()
    log.info(
        '--- STARTING TO RUN THE cl_utils.py AT %s' %
        (startTime,))

    # set options interactively if user requests
    if "interactiveFlag" in locals() and interactiveFlag:

        # load previous settings
        moduleDirectory = os.path.dirname(__file__) + "/resources"
        pathToPickleFile = "%(moduleDirectory)s/previousSettings.p" % locals()
        try:
            with open(pathToPickleFile):
                pass
            previousSettingsExist = True
        except:
            previousSettingsExist = False
        previousSettings = {}
        if previousSettingsExist:
            previousSettings = pickle.load(open(pathToPickleFile, "rb"))

        # x-raw-input
        # x-boolean-raw-input
        # x-raw-input-with-default-value-from-previous-settings

        # save the most recently used requests
        pickleMeObjects = []
        pickleMe = {}
        theseLocals = locals()
        for k in pickleMeObjects:
            pickleMe[k] = theseLocals[k]
        pickle.dump(pickleMe, open(pathToPickleFile, "wb"))

    # CALL FUNCTIONS/OBJECTS
    if read and sendToKindle:
        from headjack.read import sendToKindle
        sender = sendToKindle(
            log=log,
            settings=settings,
            dbConn=dbConn
        )
        sender.send()

    # CALL FUNCTIONS/OBJECTS
    if read and convert and kindleAnnotations:
        from headjack.read import convertKindleNB
        converter = convertKindleNB(
            log=log,
            settings=settings,
            dbConn=dbConn
        )
        converter.convert()

    if media and stage:
        from headjack.archiver import docs
        stager = docs(
            log=log,
            settings=settings,
            dbConn=dbConn
        )
        stager.stash()

    if media and archive:
        from headjack.archiver import docs
        stager = docs(
            log=log,
            settings=settings,
            dbConn=dbConn
        )
        stager.archive()
    if web2epub:
        from headjack.read import generate_web_article_epubs
        epubs = generate_web_article_epubs(
            log=log,
            settings=settings,
            dbConn=dbConn
        )
        epubs.create()
    if marvin and iimport:

        from headjack.archiver import marvin as ma
        marvin = ma(
            log=log,
            settings=settings,
            dbConn=dbConn
        )
        extractedDir = marvin.import_database(
            pathToMarvinBackup=settings["read"]["marvin_export_path"])
        if extractedDir:
            marvin.upload_marvin_images_to_flickr(
                photoDir=extractedDir + "/photos")

        marvin.trash_articles()

    if marvin and export:

        from headjack.archiver import marvin as ma
        marvin = ma(
            log=log,
            settings=settings,
            dbConn=dbConn
        )
        marvin.generate_marvin_webarticle_assets()

    if dt:

        from headjack.archiver import devonthink
        dtDB = devonthink(
            log=log,
            settings=settings,
            importFolder=pathToImportFolder,
            pathToDevonthinkDB=pathToDevonthinkDB
        )
        dtDB.ingest()

    if "dbConn" in locals() and dbConn:
        dbConn.commit()
        dbConn.close()

    ## FINISH LOGGING ##
    endTime = times.get_now_sql_datetime()
    runningTime = times.calculate_time_difference(startTime, endTime)
    log.info('-- FINISHED ATTEMPT TO RUN THE cl_utils.py AT %s (RUNTIME: %s) --' %
             (endTime, runningTime, ))

    return


if __name__ == '__main__':
    main()
