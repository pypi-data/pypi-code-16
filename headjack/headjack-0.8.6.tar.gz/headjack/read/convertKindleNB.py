#!/usr/local/bin/python
# encoding: utf-8
"""
*convert exported kindle annotations to markdown and place them alongside the PDF version of the kindle doc in a specified directory*

:Author:
    David Young

:Date Created:
    October 20, 2016
"""
################# GLOBAL IMPORTS ####################
import sys
import os
import re
import codecs
os.environ['TERM'] = 'vt100'
from fundamentals import tools
from polyglot.markdown import kindle_notebook
from fundamentals.mysql import readquery


class convertKindleNB():
    """
    *convert exported kindle annotations to markdown and place them alongside the PDF version of the kindle doc in a specified director*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary
        - ``dbConn`` -- database connection

    **Usage:**

        The kindle annotation converter relys on the following parameters in the headjack settings file:

        .. code-block:: yaml

            read:
                reading_list_root_path: XXX
                kindle_annotations_directory: XXX
                pdf_notes_directory: XXX

        Assuming you have all parameters setup in your settings file, to process your folder of Kindle annotation notebooks run the following code:

        .. code-block:: python 

            from headjack.read import convertKindleNB
            converter = convertKindleNB(
                log=log,
                settings=settings,
                dbConn=dbConn
            )
            converter.convert()   
    """
    # Initialisation

    def __init__(
            self,
            log,
            dbConn,
            settings=False,

    ):
        self.log = log
        log.debug("instansiating a new 'convertKindleNB' object")
        self.settings = settings
        self.dbConn = dbConn
        # xt-self-arg-tmpx

        # Initial Actions
        self.annotationDir = self.settings[
            "read"]["kindle_annotations_directory"]
        self.pdfNotesDir = self.settings[
            "read"]["pdf_notes_directory"]

        return None

    def convert(
            self):
        """*convert the annotations to markdown and add to PDF-notes folder alongside associated media*

        **Usage:**

            see class usage
        """
        self.log.info('starting the ``convert`` method')

        # GENERATE LIST OF ALL PDFS IN READING-LIST FOLDER
        from headjack.read import get_pdf_paths
        pdfDict = get_pdf_paths(
            log=self.log,
            settings=self.settings
        )

        # ITERATE OVER ANNOTATION FILES IN THE ANNOTATIONS EXPORT DIRECTORY
        basePath = self.annotationDir
        for d in os.listdir(basePath):
            if os.path.isfile(os.path.join(basePath, d)) and os.path.splitext(d)[1] == ".html":

                kindleHTML = os.path.join(basePath, d)

                # CONVERT HTML TO MARKDOWN
                mdOutputFilepath = self.pdfNotesDir + "/" + \
                    d.replace(".html", ".md").replace("_-_Notebook", "")
                nb = kindle_notebook(
                    log=self.log,
                    kindleExportPath=kindleHTML,
                    outputPath=mdOutputFilepath
                )
                notePath = nb.convert()

                # FIND THE ASSOCIATED PDF FILE & GRAB METADATA FROM DATABASE
                if notePath:
                    header = False
                    title = d.replace(".html", "").replace(
                        "_-_Notebook", "").replace(
                        "-_Notebook", "").replace("_", " ")
                    matchObject = re.search(r"_xx(\d*)xx", mdOutputFilepath)
                    if matchObject:
                        pdfKey = matchObject.group()
                        dbKey = matchObject.group(1)
                        sqlQuery = u"""
                            select * from `reading-list` where primaryId = %(dbKey)s
                        """ % locals()
                        rows = readquery(
                            log=self.log,
                            sqlQuery=sqlQuery,
                            dbConn=self.dbConn,
                            quiet=False
                        )
                        rows = rows[0]
                        title = rows["title"]
                        url = rows["url"]
                        author = rows["author"]

                        for pdfName, pdfPath in pdfDict.iteritems():
                            if pdfKey in pdfName:
                                subtype = pdfPath.replace(self.settings["read"][
                                                          "reading_list_root_path"], "")
                                if subtype[0] == "/":
                                    subtype = subtype[1:]
                                subtype = subtype.split("/")[0]
                                try:
                                    self.log.debug("attempting to rename file %s to %s" % (
                                        pdfPath, self.pdfNotesDir))
                                    os.rename(
                                        pdfPath, self.pdfNotesDir + "/" + pdfName)
                                except Exception, e:
                                    self.log.error(
                                        "could not rename file %s to %s - failed with this error: %s " % (pdfPath, pdfPath, str(e),))
                                    sys.exit(0)
                                header = u"""databaseid: %(dbKey)s 
pdfName: %(pdfName)s
title: %(title)s
subtype: %(subtype)s
author: %(author)s
url: %(url)s 
shareText: 
rating: 
tags: 
action: delete|archive""" % locals()

                    if not header:
                        import urllib
                        url = "https://www.google.co.uk/#q=" + \
                            urllib.quote(title)
                        header = u"""title: %(title)s
url: %(url)s 
subtype: book
shareText: 
rating: 
tags: 
action: delete|archive""" % locals()

                    # ADD HEADER TO THE MARKDOWN OUTPUT
                    pathToReadFile = mdOutputFilepath
                    try:
                        self.log.debug(
                            "attempting to open the file %s" % (pathToReadFile,))
                        readFile = codecs.open(
                            pathToReadFile, encoding='utf-8', mode='r')
                        thisData = readFile.read()
                        readFile.close()
                    except IOError, e:
                        message = 'could not open the file %s' % (
                            pathToReadFile,)
                        self.log.critical(message)
                        raise IOError(message)

                    thisData = header + "\n" + thisData

                    pathToWriteFile = mdOutputFilepath
                    try:
                        self.log.debug("attempting to open the file %s" %
                                       (pathToWriteFile,))
                        writeFile = codecs.open(
                            pathToWriteFile, encoding='utf-8', mode='w')
                    except IOError, e:
                        message = 'could not open the file %s' % (
                            pathToWriteFile,)
                        self.log.critical(message)
                        raise IOError(message)

                    writeFile.write(thisData)
                    writeFile.close()

                    # TRASH THE KINDLE EXPORT
                    trash = self.annotationDir + "/trash"
                    # Recursively create missing directories
                    if not os.path.exists(trash):
                        os.makedirs(trash)
                    basename = os.path.basename(kindleHTML)
                    destination = 'pathToDestination'
                    os.rename(kindleHTML, trash + "/" + basename)

        self.log.info('completed the ``convert`` method')
        return None

    # use the tab-trigger below for new method
    # xt-class-method
