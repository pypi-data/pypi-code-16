#!/usr/local/bin/python
# encoding: utf-8
"""
*methods for importing and processing marvin export data*

:Author:
    David Young

:Date Created:
    February 12, 2017
"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
import zipfile
import shutil
import codecs
import yaml
from datetime import datetime, date, time
from picaxe import picaxe
from polyglot import printpdf, webarchive
from polyglot.markdown import translate
from fundamentals import tools
from fundamentals.mysql import sqlite2mysql, writequery, readquery, directory_script_runner


class marvin():
    """
    *The worker class for the marvin module*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary
        - ``dbConn`` -- the headjack database connection

    **Usage:**

        To setup your logger, settings and database connections, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_). 

        To initiate a marvin object, use the following:

        .. todo::

            - add a tutorial about ``marvin`` to documentation
            - create a blog post about what ``marvin`` does

        .. code-block:: python 

            from headjack.archiver import  as ma
            marvin = ma(
                log=log,
                settings=settings,
                dbConn=dbConn
            )   
    """

    def __init__(
            self,
            log,
            dbConn,
            settings=False
    ):
        self.log = log
        log.debug("instansiating a new 'marvin' object")
        self.settings = settings
        self.dbConn = dbConn
        # xt-self-arg-tmpx

        # INITIAL ACTIONS - RUN SQL SCRITPS TO IMPORT AND TIDY MARVIN DATABASE
        # CONTENT
        pathToScriptDirectory = os.path.dirname(__file__) + "/resources/mysql"
        directory_script_runner(
            log=self.log,
            pathToScriptDirectory=pathToScriptDirectory,
            databaseName=self.settings["database settings"]["db"],
            loginPath=self.settings["database settings"]["loginPath"],
            waitForResult=True,
            successRule=False,
            failureRule=False
        )

        # INITIALISE FLICKR OBJECT TO UPLOAD PHOTOS LATER
        self.flickr = picaxe(
            log=self.log,
            settings=self.settings
        )

        return None

    def import_database(
            self,
            pathToMarvinBackup):
        """
        *extract the marvin zip file and import the contained sqlite database into headjack's mysql database*

        **Key Arguments:**
            - ``pathToMarvinBackup`` -- the path to the backup zip file from marvin

        **Return:**
            - ``extractedDir`` -- the path to the directory containing the extracted marvin backup data

        **Usage:**

            To import the marvin database (exported from the marvin iOS app - see tutorial for how-to instructions):

            .. code-block:: python 

                extractedDir = marvin.import_database(
                    pathToMarvinBackup="path/to/marvin.m3backup") 
        """
        self.log.info('starting the ``import_database`` method')

        # TEST THE DATABASE EXPORT EXISTS AT GIVEN LOCATION
        exists = os.path.exists(pathToMarvinBackup)
        if not exists:
            print "Cannot locate the Marvin export"
            return

        # EXTRACT INTO TMP
        zip_ref = zipfile.ZipFile(pathToMarvinBackup, 'r')
        now = datetime.now()
        now = now.strftime("%Y%m%dt%H%M%S")
        extractedDir = "/tmp/marvin_%(now)s" % locals()
        if not os.path.exists(extractedDir):
            os.makedirs(extractedDir)
        zip_ref.extractall(extractedDir)
        zip_ref.close()

        # IMPORT THE SQLITE DATABASE TABLES INTO HEADJACK MYSQL DATABASE
        converter = sqlite2mysql(
            log=self.log,
            settings=self.settings,
            pathToSqlite=extractedDir + "/MainDB.v3.sqlite",
            tablePrefix="Marvin"
        )
        converter.convert_sqlite_to_mysql()

        # DELETE THE COMPRESSED MARVIN BACKUP FILE
        os.remove(pathToMarvinBackup)

        self.log.info('completed the ``import_database`` method')
        return extractedDir

    def upload_marvin_images_to_flickr(
            self,
            photoDir):
        """*upload marvin images to flickr and add the flickr MMD image-link back into the headjack database (`web_article_annotations` table)*

        **Key Arguments:**
            - ``photoDir`` -- the path to the directory of extracted marvin photos

        **Usage:**

            To upload photos found in the marvin export to flickr and copy the MMD image-links back into the headjack database at the correct location in the epub's annotation log (``web_article_annotations`` table):

            .. code-block:: python 

                marvin.upload_marvin_images_to_flickr(
                    photoDir=extractedDir+"/photos") 
        """
        self.log.info('starting the ``upload_marvin_images_to_flickr`` method')

        # SELECT THE PHOTOS THAT NEED ADDED TO FLICKR
        sqlQuery = u"""
            select * from web_article_annotations a, web_articles w, Marvin_Tags t where a.articleId=w.primaryId and a.photoUUID=t.EntryUUID and a.photoUUID is not null and a.flickrPhotoId is null;
        """ % locals()
        rows = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.dbConn,
            quiet=False
        )

        # GRAB THE METADATA REQUIRED FOR EACH IMAGE
        allPhotos = {}
        for r in rows:
            if r["photoUUID"] not in allPhotos:
                allPhotos[r["photoUUID"]] = {
                    "book": r["title"],
                    "url": r["url"],
                    "title": r["annotation"].split("\n")[0].strip(),
                    "description": ("\n").join(r["annotation"].split("\n")[1:]).strip(),
                    "tags": r["Tag"].replace(" ", "-").lower(),
                    "articleId": r["primaryId"]
                }
            else:
                allPhotos[r["photoUUID"]]["tags"] += ", " + r["Tag"].lower()

        # GRAB PATHS TO ALL OF THE EXPORTED PHOTO FILES
        photoPaths = []
        for d in os.listdir(photoDir):
            if os.path.isfile(os.path.join(photoDir, d)):
                photoPaths.append(os.path.join(photoDir, d))

        # MATCH PHOTO METADATA WITH THEIR FILES
        for k, d in allPhotos.iteritems():
            UUID = k
            for p in photoPaths:
                title = False
                description = False
                if UUID in p:

                    if len(d["title"]):
                        title = d["title"]
                    book = d["book"]
                    url = d["url"]
                    description = d["description"] + \
                        "\n\nFrom the article <em>'%(book)s'</em>\n%(url)s" % locals(
                    )

                    # UPLOAD PHOTO
                    photoid = self.flickr.upload(
                        imagePath=p,
                        title=title,
                        private=True,
                        tags=d["tags"],
                        description=description,
                        imageType="image",  # image|screengrab|photo
                        album="web-article images",
                        openInBrowser=False
                    )
                    mdLink = self.flickr.md(
                        url=photoid,
                        # [75, 100, 150, 240, 320, 500, 640, 800, 1024, 1600, 2048]
                        width="original"
                    )
                    mdLink = mdLink.replace('"', '\\"')
                    print "%(p)s uploaded to flickr (*%(title)s*)" % locals()

                    # UPDATE THE HEADJACK DATABASE WITH IMAGE LINKS
                    sqlQuery = """update web_article_annotations set flickrPhotoId = %(photoid)s, flickrMMDImageLink = "%(mdLink)s" where photoUUID = "%(UUID)s" """ % locals(
                    )
                    writequery(
                        log=self.log,
                        sqlQuery=sqlQuery,
                        dbConn=self.dbConn
                    )

        self.log.info(
            'completed the ``upload_marvin_images_to_flickr`` method')
        return None

    def generate_marvin_webarticle_assets(
            self):
        """*generate assets associated with the web-article*

        **Usage:**

            To create the assests associated with the web-article being archived (webarchive, PDF, yaml, MMD annotations) run the following:

            .. code-block:: python 

                marvin.generate_marvin_webarticle_assets()
        """
        self.log.info(
            'starting the ``generate_marvin_webarticle_assets`` method')

        devonthinkFolder = self.settings["devonthink"][
            "import_folder"] + "/web-articles"

        # FIND THE WEB-ARTICLES THAT HAVE BEEN READ BUT NOT ARCHIVED
        sqlQuery = u"""
            SELECT * from web_articles where workflowStage = "read" and rating > 1;
        """ % locals()
        books = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.dbConn
        )

        # GENEATE THE WEB-ASSESTS IN THE DEVONTHINK IMPORT FOLDER
        for b in books:
            webarticleId = b["primaryId"]
            # RECURSIVELY CREATE MISSING DIRECTORIES
            exportDir = devonthinkFolder + "/" + b["title"]
            if not os.path.exists(exportDir):
                os.makedirs(exportDir)

            # GENERATE PDF OF THE WEB-PAGE
            pdf = printpdf(
                log=self.log,
                settings=self.settings,
                url=b["url"],
                folderpath=exportDir,
                title=b["title"],
                readability=True
            ).get()

            # GENERATE THE WEBARCHIVE
            wa = webarchive(
                log=self.log,
                settings=self.settings
            )
            wa.create(url=b["url"],
                      pathToWebarchive=exportDir + "/" + b["title"] + ".webarchive")

            # GET ARTICLE TAGS
            sqlQuery = u"""
                SELECT tag FROM web_article_tags where articleId=%(webarticleId)s;
            """ % locals()
            rows = readquery(
                log=self.log,
                sqlQuery=sqlQuery,
                dbConn=self.dbConn
            )
            tags = []
            tags[:] = [str(t["tag"].lower().replace(" ", "-")) for t in rows]

            # GENERATE THE MMD ANNOTATION DOC
            mmdContent = self._convert_annotations_to_mmd_content(
                webarticleId, tags)

            pathToMMDFile = exportDir + "/" + b["title"] + ".md"
            try:
                self.log.debug("attempting to open the file %s" %
                               (pathToMMDFile,))
                writeFile = codecs.open(
                    pathToMMDFile, encoding='utf-8', mode='w')
            except IOError, e:
                message = 'could not open the file %s' % (pathToMMDFile,)
                self.log.critical(message)
                raise IOError(message)
            writeFile.write(mmdContent.encode(
                "utf-8").replace("\n\n\n", "\n\n").replace("\n\n\n", "\n\n").replace("\n\n\n", "\n\n"))
            writeFile.close()

            # GENERATE THE YAML CONTENT
            yamlContent = {
                "title": str(b["title"]),
                "rating": b["rating"],
                "url": str(b["url"]),
                "kind": "web-articles",
                "tags": tags
            }

            fileName = exportDir + "/" + b["title"] + ".yaml"
            stream = file(fileName, 'w')
            yamlContent = yamlContent
            yaml.dump(yamlContent, stream, default_flow_style=False)
            stream.close()

            # MOVE THE EPUB DOC
            epubPath = self.settings["dropbox_root"] + "/" + b["dropboxPath"]
            exists = os.path.exists(epubPath)
            if exists:
                basename = os.path.basename(epubPath)
                os.rename(epubPath, exportDir + "/" + basename)

            sqlQuery = """update web_articles set workflowStage = "archived" where primaryId = %(webarticleId)s""" % locals(
            )
            writequery(
                log=self.log,
                sqlQuery=sqlQuery,
                dbConn=self.dbConn
            )

        self.log.info(
            'completed the ``generate_marvin_webarticle_assets`` method')
        return None

    def _convert_annotations_to_mmd_content(
            self,
            webarticleId,
            tags):
        """*convert marvin annotations to mmd content*

        **Key Arguments:**
            - ``webarticleId`` -- the ID of the webarticle in the database.
            - ``tags`` -- the webarticle tags

        **Return:**
            - ``content`` -- the MMD content of the annotation file to be written
        """
        self.log.info(
            'starting the ``_convert_annotations_to_mmd_content`` method')

        content = []
        md = translate(
            log=self.log,
            settings=self.settings
        )

        sqlQuery = u"""
            SELECT * FROM web_articles where primaryId=%(webarticleId)s;
        """ % locals()
        meta = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.dbConn
        )[0]

        tags = (", ").join(tags)

        title = meta["title"]
        rating = meta["rating"]
        url = meta["url"]

        frontMatter = """---
title: %(title)s 
rating: %(rating)s
link: %(url)s 
tags: [%(tags)s]
---\n\n""" % locals()
        content.append(frontMatter)
        content.append(md.header(meta["title"], 1))

        citation = md.cite(
            title=title,
            author=meta["author"],
            year=False,
            url=url,
            publisher=False,
            mediaKind="web-article",
            linkedText=False,
            nocite=True
        )
        content.append(citation)

        sqlQuery = u"""
            SELECT * FROM web_article_annotations where articleId=%(webarticleId)s order by annotationIndex;
        """ % locals()
        rows = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.dbConn
        )

        for a in rows:
            annotation = a["annotation"]
            image = a["flickrMMDImageLink"]
            if not annotation:
                continue
            if a["markupType"] == "p":
                content.append(annotation)
            elif a["markupType"] == "image":
                content.append(image)
            elif a["markupType"] == "bold":
                content.append(md.bold(annotation))
            elif a["markupType"] == "header":
                content.append(md.header(annotation, level=2))
            elif a["markupType"] == "blockquote":
                content.append(md.blockquote(annotation))
            elif a["markupType"] == "code-block":
                content.append(md.codeblock(annotation))
            elif a["markupType"] == "code":
                content.append(md.code(annotation))
            elif a["markupType"] == "emphasis":
                content.append(md.em(annotation))
            elif a["markupType"] == "note":
                content.append(md.definition("note", annotation))
            elif a["markupType"] == "footnote":
                content.append(md.footnote(annotation))

        self.log.info(
            'completed the ``_convert_annotations_to_mmd_content`` method')
        return ("  \n\n").join(content)

    def trash_articles(
            self):
        """*trash articles with a rating of 1*

        **Usage:**

            To trash articles with a rating of 1:

            .. code-block:: python 

                marvin.trash_articles()
        """
        self.log.info('starting the ``trash_articles`` method')

        sqlQuery = u"""
            SELECT * from web_articles where workflowStage = "read" and rating = 1; 
        """ % locals()
        books = readquery(
            log=self.log,
            sqlQuery=sqlQuery,
            dbConn=self.dbConn
        )

        # GENEATE THE WEB-ASSESTS IN THE DEVONTHINK IMPORT FOLDER
        for b in books:
            webarticleId = b["primaryId"]

            # MOVE THE EPUB DOC
            epubPath = self.settings["dropbox_root"] + "/" + b["dropboxPath"]
            exists = os.path.exists(epubPath)
            if exists:
                os.remove(epubPath)

            sqlQuery = """update web_articles set workflowStage = "trashed" where primaryId = %(webarticleId)s""" % locals(
            )
            writequery(
                log=self.log,
                sqlQuery=sqlQuery,
                dbConn=self.dbConn
            )

        self.log.info('completed the ``trash_articles`` method')
        return None

    # use the tab-trigger below for new method
    # xt-class-method
