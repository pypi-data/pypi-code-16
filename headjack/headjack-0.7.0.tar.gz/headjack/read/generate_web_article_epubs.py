#!/usr/local/bin/python
# encoding: utf-8
"""
*query the database for new web-articles and generate epub versions of the content to be read later*

:Author:
    David Young

:Date Created:
    January  5, 2017
"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
from fundamentals import tools
from fundamentals.mysql import readquery, writequery
from polyglot import ebook


class generate_web_article_epubs():
    """
    *an epub generator - query the database for new web-articles and generate epub versions of the content to be read later*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary
        - ``dbConn`` -- the database connections

    **Usage:**

        To setup your logger, settings and database connections, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_). 

        To initiate a generate_web_article_epubs object, use the following:

        .. todo::

            - update the package tutorial if needed

        To query the database and generate epubs for the next 10 web-articles requested, run the code:

        .. code-block:: python 

            from headjack.read import generate_web_article_epubs
            epubs = generate_web_article_epubs(
                log=log,
                settings=settings,
                dbConn=dbConn
            )
            epubs.create()   
    """
    # INITIALISATION

    def __init__(
            self,
            log,
            dbConn,
            settings=False,

    ):
        self.log = log
        log.debug("instansiating a new 'generate_web_article_epubs' object")
        self.settings = settings
        self.dbConn = dbConn
        # xt-self-arg-tmpx

        return None

    def create(self):
        """
        *generate the epubs from the web-articles*
        """
        self.log.info('starting the ``create`` method')

        # REQUEST THE WEB-ARTICLE URLS AND METADATA
        webArticles = self._get_data_to_send()

        for w in webArticles:
            if not w["subtype"]:
                w["subtype"] = "article"
            outputDirectory = self.settings["read"][
                "reading_list_root_path"] + "/web-articles/" + w["subtype"]
            # RECURSIVELY CREATE MISSING DIRECTORIES
            if not os.path.exists(outputDirectory):
                os.makedirs(outputDirectory)
            print w["url"]
            epub = ebook(
                log=self.log,
                settings=self.settings,
                urlOrPath=w["url"],
                title=False,
                bookFormat="epub",
                outputDirectory=outputDirectory,
                header=False,
                footer=False
            )
            pathToEpub = epub.get()

            # TEST IF EPUB HAS BEEN GENERATED AND UPDATE BOOKKEEPING COLUMNS IN
            # DATABASE
            primaryId = w["primaryId"]
            if pathToEpub and os.path.exists(pathToEpub):

                sqlQuery = u"""
                    update web_articles set epubCreated = now() where primaryId = %(primaryId)s 
                """ % locals()
            else:
                url = w["url"]
                self.log.warning(
                    'the epub of the article %(url)s was not generated for some reason' % locals())
                sqlQuery = u"""
                    update web_articles set epubCreated = 0 where primaryId = %(primaryId)s 
                """ % locals()
            writequery(
                log=self.log,
                sqlQuery=sqlQuery,
                dbConn=self.dbConn
            )

        self.log.info('completed the ``create`` method')
        return generate_web_article_epubs

    def _get_data_to_send(
            self):
        """*Select the rows from the web_articles table in the database containing webarticles that need converted to epub*

        **Return:**
            - ``data`` -- a list of dictionaries giving details of the data used to generate the epub books
        """
        self.log.info('starting the ``_get_data_to_send`` method')

        sqlQuery = u"""
            select * from web_articles where epubCreated is null order by dateCreated limit 10
        """ % locals()

        data = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.dbConn,
            quiet=False
        )

        self.log.info('completed the ``_get_data_to_send`` method')
        return data

    # xt-class-method
