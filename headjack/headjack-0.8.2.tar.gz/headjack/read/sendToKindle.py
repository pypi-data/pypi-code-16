#!/usr/local/bin/python
# encoding: utf-8
"""
*send PDF and web-articles to your kindle and/or kindle apps*

:Author:
    David Young

:Date Created:
    September 30, 2016
"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
from fundamentals import tools
from polyglot import htmlCleaner
import codecs
from fundamentals.mysql import readquery, writequery
from subprocess import Popen, PIPE, STDOUT


class sendToKindle():
    """
    Convert and send webarticles and PDF files found in the reading-list table to the user's kindle device and/or iOS apps

    **Key Arguments:**
        - ``dbConn`` -- mysql database connection
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary

    **Usage:**
        .. todo::

            add usage info

        To send new reading list items to kindle, add the code:

        .. code-block:: python

            from headjack.read import sendToKindle
            sender = sendToKindle(
                log=log,
                settings=settings,
                dbConn=dbConn
            )
            sender.send()

    """
    # Initialisation

    def __init__(
            self,
            log,
            dbConn=False,
            settings=False,

    ):
        self.log = log
        log.debug("instansiating a new 'sendToKindle' object")
        self.dbConn = dbConn
        self.settings = settings
        self.pdfs = []
        # xt-self-arg-tmpx

        # Initial Actions

        return None

    def send(self):
        """Send to items to kindle

        **Return:**
            - None

        See class for usage
        """
        self.log.info('starting the ``send`` method')

        self.send_pdfs()
        self.send_webarticles()

        self.log.info('completed the ``send`` method')
        return None

    def _get_data_to_send(
            self,
            docType):
        """*Select the rows from the reading-list table in the database containing webarticles or PDFs that need sent to kindle device and/or apps*

        **Key Arguments:**
            - ``docType`` -- either PDFs of webpages. [pdf|web]

        **Return:**
            - ``data`` -- a list of dictionaries giving details of the data to send to kindle
        """
        self.log.info('starting the ``_get_data_to_send`` method')

        if docType == "pdf":
            sqlQuery = u"""
                select * from `reading-list` where  kind = "imported-pdf" and sentToKindle =0 and workflowStage = "reading" and pdfName is not null order by dateCreated limit 30
            """ % locals()
        elif docType == "web":
            sqlQuery = u"""
                select * from `reading-list` where  kind = "webpage" and sentToKindle =0 and workflowStage = "reading" and pdfName is not null order by dateCreated limit 10
            """ % locals()

        data = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.dbConn,
            quiet=False
        )

        self.log.info('completed the ``_get_data_to_send`` method')
        return data

    def _update_database_for_sent_item(
            self,
            primaryId,
            success):
        """*update the database to indicate that the PDFs have been sent to kindle(s)*


        **Key Arguments:**
            - ``primaryId`` -- unique ID of database entry to update
            - ``success`` -- success message/number

        **Return:**
            - None
        """
        self.log.info(
            'starting the ``__update_database_for_sent_item`` method')

        if success == True:
            sqlQuery = u"""
                update `reading-list` set sentToKindle = 1 where primaryId = %(primaryId)s
            """ % locals()
            writequery(
                log=self.log,
                sqlQuery=sqlQuery,
                dbConn=self.dbConn
            )
        elif success == 404:
            sqlQuery = u"""
                update `reading-list` set sentToKindle = -1 where primaryId = %(primaryId)s
            """ % locals()
            writequery(
                log=self.log,
                sqlQuery=sqlQuery,
                dbConn=self.dbConn
            )

        self.log.info(
            'completed the ``__update_database_for_sent_item`` method')
        return None

    def _trigger_docx_generation(
            self,
            pdfPath):
        """*Trigger the generation of docx version from imported PDFs*

        Note it is up to the user to generate a DOCX version of the PDF as there are no good open-source command-line tools for *unix that accurately convert PDF to DOCX.

        This method will look for a docx version of the PDF in the same folder as thee PDF. If it doesn't find one it will add a `.hj` placeholder file in the same folder. If it does find a docx file, it will remove any `.hj` placeholder for the file.

        For example, if we have a PDF called `headjack-documentation.pdf`, this method looks for `headjack-documentation.docx` in the same folder. If it doesn't find `headjack-documentation.docx` it creates a `headjack-documentation.hj` placeholder file, but if it does find the docx it will delete `headjack-documentation.hj`.

        **Key Arguments:**
            - ``pdfPath`` -- path to the input PDF file
        """
        self.log.info('starting the ``_trigger_docx_generation`` method')

        docxPath = pdfPath.replace(".pdf", ".docx")
        hjPath = pdfPath.replace(".pdf", ".hj")

        exists = os.path.exists(docxPath)
        if exists:
            try:
                os.remove(hjPath)
            except Exception as e:
                pass
            print "FOUND %(docxPath)s " % locals()
            return docxPath
        else:
            writeFile = codecs.open(hjPath, encoding='utf-8', mode='w')
            writeFile.close()
            print "NOT FOUND, %(hjPath)s created" % locals()
            return False

        self.log.info('completed the ``_trigger_docx_generation`` method')
        return None

    def send_pdfs(
            self):
        """*send pdfs*

        **Key Arguments:**
            # -

        **Return:**
            - None

        **Usage:**
            ..  todo::

                - add usage info
                - create a sublime snippet for usage
                - update package tutorial if needed

            .. code-block:: python

                usage code

        """
        from headjack.read import get_pdf_paths
        self.log.info('starting the ``send_pdfs`` method')

        pdfsToSend = self._get_data_to_send(docType="pdf")

        pdfDict = get_pdf_paths(
            log=self.log,
            settings=self.settings
        )

        for pdf in pdfsToSend:

            # TEST IF REFLOW REQUIRED
            if pdf["pdfName"] in pdfDict:
                docx = self._trigger_docx_generation(pdfDict[pdf["pdfName"]])
                if docx:
                    articleId = pdf["primaryId"]
                    original = pdf["url"]
                    footer = """%(articleId)s | <a href="%(original)s">search for original webpage</a>""" % locals(
                    )
                    from polyglot import kindle
                    sender = kindle(
                        log=self.log,
                        settings=self.settings,
                        urlOrPath=docx,
                        title=pdf["pdfName"].replace(
                            ".pdf", "").replace("_", " "),
                        header=footer,
                        footer=footer
                    )
                    success = sender.send()

                    if success == True or success == 404:
                        self._update_database_for_sent_item(
                            articleId, success)
                        os.remove(docx)

        self.log.info('completed the ``send_pdfs`` method')
        return None

    def send_webarticles(
            self):
        """*Send all new webarticles found in the reading-list database table to kindle device and/or apps*

        **Return:**
            - None

        **Usage:**

            To send only the webarticles (not imported PDFs) to your kindle run the code: 

            .. code-block:: python

                from headjack.read import sendToKindle
                sender = sendToKindle(
                    log=log,
                    settings=settings,
                    dbConn=dbConn
                )
                sender.send_webarticles()

        """
        self.log.info('starting the ``send_webarticles`` method')

        articlesToSend = self._get_data_to_send(docType="web")

        for article in articlesToSend:

            articleId = article["primaryId"]
            original = article["url"]
            footer = """%(articleId)s""" % locals(
            )

            from polyglot import kindle
            sender = kindle(
                log=self.log,
                settings=self.settings,
                urlOrPath=article["url"],
                title=article["pdfName"].replace(".pdf", "").replace("_", " "),
                header=footer,
                footer=footer
            )
            success = sender.send()

            if success == True or success == 404:
                self._update_database_for_sent_item(
                    article["primaryId"], success)

        self.log.info('completed the ``send_webarticles`` method')
        return None
