#!/usr/local/bin/python
# encoding: utf-8
"""
import-pdfs-into-papers.py
==========================
:Summary:
    Import PDFs into Papers.app for Mac.

:Author:
    David Young

:Date Created:
    February 9, 2016

Usage:
    import-pdfs-into-papers <pdfFolderPath> [-s <pathToSettingsFile>]

    -h, --help            show this help message
    -v, --version         show version
"""

## USER DEFINED VARIABLES - ONLY PLACE THIS SCRIPT NEEDS MODIFIED ##

################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
import readline
import glob
import markdown as md
import re
from subprocess import Popen, PIPE, STDOUT
import docopt
import yaml
from dryxPython import mysql as dms
from fundamentals import tools, times

import codecs


def handler(e):
    return (u' ', e.start + 1)
codecs.register_error('dryx', handler)


def main(arguments=None):
    """
    *The main function used when ``import-pdfs-into-papers.py`` is run as a single script from the cl, or when installed as a cl command*
    """

    # setup the command-line util settings
    su = tools(
        arguments=arguments,
        docString=__doc__,
        logLevel="DEBUG",
        options_first=False,
        projectName="muppet"
    )
    arguments, settings, log, dbConn = su.setup()

    # UNPACK REMAINING CL ARGUMENTS USING `EXEC` TO SETUP THE VARIABLE NAMES
    # AUTOMATICALLY
    for arg, val in arguments.iteritems():
        if arg[0] == "-":
            varname = arg.replace("-", "") + "Flag"
        else:
            varname = arg.replace("<", "").replace(">", "")
        if isinstance(val, str) or isinstance(val, unicode):
            exec(varname + " = '%s'" % (val,))
        else:
            exec(varname + " = %s" % (val,))
        if arg == "--dbConn":
            dbConn = val
        log.debug('%s = %s' % (varname, val,))

    # CREATE APPLESCRIPT RETURN STRING WITH THE DETAILS I WANT
    asProperties = {
        "abstract": "abstract",
        "title": "title",
        "tags": "keyword names",
        "papersId": "id",
        "papersUrl": "item url",
        "author": "author names",
        "subtype": "subtitle",
        "rating": "my rating",
        "url": "publication url",
        "path": "full path of primary file item",
        "reference": "formatted reference",
        "originalPath": "original path of primary file item"
    }
    returnString = "return "
    for i, v in enumerate(asProperties.values()):
        if i + 1 == len(asProperties):
            returnString += """ %(v)s of thisItem""" % locals()
        else:
            returnString += """ %(v)s of thisItem & "||" & """ % locals()

            elif action == "archive":

                if len(inputMetadata["tags"]) == 0:
                    print "%(filePath)s needs tags added" % locals()
                    continue

                outputMetadata = import_media_and_return_metadata(
                    log=log,
                    mediaPath=pdfPath,
                    returnString=returnString,
                    asProperties=asProperties,
                )

                # CHECK FILE WAS INDEED IMPORTED
                if outputMetadata["originalPath"] != pdfPath:
                    originalPath = outputMetadata["originalPath"]
                    log.error(
                        'this is not the original file: "%(originalPath)s" ' % locals())
                    sys.exit(0)

                else:
                    updates = ""
                    sqlUpdates = ""
                    sqlTags = ""
                    thisId = outputMetadata["papersId"]
                    for k, v in inputMetadata.iteritems():
                        if k == "tags":
                            tags = v.split(",")
                            for tag in tags:
                                tag = tag.strip().lower().replace(" ", "-")
                                updates += """
                                    set this to (make new keyword item with properties {name:"%(tag)s"})
                                    add keywords {this} to thisItem
                                """ % locals()
                                sqlTags += """insert ignore into `media-tags` (mediaTable,mediaId,tag) values("reading-list", %(databaseid)s , "%(tag)s");\n""" % locals(
                                )
                        else:
                            if k in asProperties:
                                prop = asProperties[k]
                                updates += """set %(prop)s of thisItem to "%(v)s"\n""" % locals()
                                if len(sqlUpdates):
                                    sqlUpdates += """, %(k)s = "%(v)s" """ % locals(
                                    )
                                else:
                                    sqlUpdates += """update `reading-list`  set %(k)s = "%(v)s" """ % locals(
                                    )

                    if len(thisData):
                        import pyperclip
                        pyperclip.copy(thisData)

                    applescript = u"""
                        tell application "Papers"
                            repeat with i from (count of publication items) to 1 by -1
                                if id of item i of publication items is equal to "%(thisId)s" then
                                    set thisItem to item i of publication items
                                    exit repeat
                                end if
                            end repeat
                            %(updates)s

                            set m to selected mode of front library window
                            set selected mode of front library window to Library Mode
                            tell front library window to set selected publications to (thisItem)
                            set i to selected inspector tab of front library window
                            set selected inspector tab of front library window to Notes Tab

                            set papersId to id of thisItem
                    
                            end tell

                        tell application "System Events"
                            activate
                            set the_results to (display dialog "Paste notes to 'General Note' section on the right" buttons {"cancel", "skip", "notes added"} default button "skip")
                            set BUTTON_Returned to button returned of the_results
                            
                            if ((BUTTON_Returned) is equal to "notes added") then
                                set BUTTON_Returned to papersId
                            end if
                            return BUTTON_Returned

                        end tell
                """ % locals()

                    cmd = "\n".join(
                        ["osascript << EOT", applescript, "EOT"])
                    p = Popen(cmd, stdout=PIPE,
                              stdin=PIPE, shell=True)
                    output = p.communicate()[0].strip()

                    if output.lower() == "cancel":
                        print "user cancelled the import script"
                        sys.exit(0)
                    elif output.lower() == "skip":
                        continue
                    elif "error" in output.lower():
                        print output
                        sys.exit(0)
                    elif len(output) == 0:
                        print "Error in applescript:\n"
                        print applescript
                        sys.exit(0)

                    papersId = output
                    if databaseid and databaseid.lower() != "false":
                        sqlUpdates += """, papersId = "%(papersId)s", workflowStage = "archived", notes = "%(thisData)s"  where primaryId = %(databaseid)s """ % locals()
                        dms.execute_mysql_write_query(
                            sqlQuery=sqlUpdates,
                            dbConn=dbConn,
                            log=log
                        )
                        dms.execute_mysql_write_query(
                            sqlQuery=sqlTags,
                            dbConn=dbConn,
                            log=log
                        )
                    # Recursively create missing directories
                    if not os.path.exists(pdfFolderPath + "/trash"):
                        os.makedirs(pdfFolderPath + "/trash")
                    try:
                        source = filePath
                        destination = ("/").join(filePath.split("/")
                                                 [0:-1]) + "/trash/" + filePath.split("/")[-1]
                        log.debug("attempting to rename file %s to %s" %
                                  (source, destination))
                        os.rename(source, destination)
                    except Exception, e:
                        log.error("could not rename file %s to %s - failed with this error: %s " %
                                  (source, destination, str(e),))
                        sys.exit(0)
                    try:
                        source = pdfPath
                        destination = ("/").join(pdfPath.split("/")
                                                 [0:-1]) + "/trash/" + pdfPath.split("/")[-1]
                        log.debug("attempting to rename file %s to %s" %
                                  (source, destination))
                        os.rename(source, destination)
                    except Exception, e:
                        log.error("could not rename file %s to %s - failed with this error: %s " %
                                  (source, destination, str(e),))
                        sys.exit(0)

    return


def import_media_and_return_metadata(
        log,
        mediaPath,
        returnString,
        asProperties):
    """*summary of function*

    **Key Arguments:**
        - ``log`` -- logger
        - ``mediaPath`` -- the path to the media file to import.
        -
        - ``returnString`` -- formated applescript string of properties to return
        - ``asProperties`` -- applescript properties to parse from returned values

    **Return:**
        - ``outputMetadata`` -- the metadata for the paper

    **Usage:**
        ..todo::

            add usage info
            create a sublime snippet for usage

        .. code-block:: python 

            usage code            
    """
    log.info('starting the ``import_media_and_return_metadata`` function')

    # IMPORT THE MEDIA FILE INTO PAPERS AND RETURN METADATA
    applescript = u"""
            tell application "Papers"
                activate
                open POSIX file "%(mediaPath)s"
                set oneHrAgo to (current date) - (60 * 60)
                set theseItems to publication items whose import date comes after oneHrAgo
                
                set the index_list to {}
                set the sorted_list to {}
                repeat (the number of items in theseItems) times
                    set the high_item to ""
                    repeat with i from 1 to (number of items in theseItems)
                        if i is not in the index_list then
                            set this_item to item i of theseItems
                            if the high_item is "" then
                                set the high_item to this_item
                                set the high_item_index to i
                            else if import date of this_item comes after the import date of high_item then
                                set the high_item to this_item
                                set the high_item_index to i
                            end if
                        end if
                    end repeat
                    set the end of sorted_list to the high_item
                    set the end of the index_list to the high_item_index
                end repeat
                    
                set thisItem to first item in sorted_list
                %(returnString)s
            end tell
    """ % locals()

    cmd = "\n".join(
        ["osascript << EOT", applescript, "EOT"])
    p = Popen(cmd, stdout=PIPE, stdin=PIPE, shell=True)
    output = p.communicate()[0].split("||")

    outputMetadata = {}
    for val, key in zip(output, asProperties.keys()):
        # RECODE INTO ASCII
        val = val.decode("utf-8")
        val = val.encode("ascii", "dryx")
        outputMetadata[key] = val.replace(
            ", ", "").replace('"', '\"').replace("'", "\'")

    log.info('completed the ``import_media_and_return_metadata`` function')
    return outputMetadata

    # use the tab-trigger below for new function
    # xt-def-with-logger

if __name__ == '__main__':
    main()
