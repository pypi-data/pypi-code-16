#!/usr/local/bin/python
# encoding: utf-8
"""
*archive media to a devonthink database*

:Author:
    David Young

:Date Created:
    January  4, 2017
"""
################# GLOBAL IMPORTS ####################
import sys
import os
import shutil
import re
import webbrowser
from subprocess import Popen, PIPE, STDOUT
import yaml
os.environ['TERM'] = 'vt100'
from fundamentals import tools


class devonthink():
    """
    *Import media content organinsed by media-kind into a devonthink database and update associate meteadata fields*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary
        - ``importFolder`` -- path to the devonthink import folder
        - ``pathToDevonthinkDB`` -- path to the devonthink database you wish to import the media into

    **Usage:**

        To setup your logger, settings and database connections, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_).

        To initiate a 'devonthink' object, use the following:

        .. code-block:: python

            from headjack.archiver import devonthink
            dtDB = devonthink(
                log=log,
                settings=settings,
                importFolder="/path/to/import/folder",
                pathToDevonthinkDB="/path/to/mydatabase.dtBase2"
            )

        The media content to be imported into devonthink must be organised in the import folder in a specific manner:

        .. image:: https://i.imgur.com/x7VCSFv.png
            :width: 800px

        The content is added to a folder whose name indicates the kind of media-content contained (e.g. 'web-articles', 'podcasts' etc). The content itself is a folder named with the title of the content (e.g. a web-article called 'Volkswagen - Wikipedia'). The folder contains files related to the content (e.g. the web-article in webarchive, epub and PDF format and a markdown file of notes). Finally there is a yaml file containing a rating, tags etc.

        .. code-block:: yaml

            title: Volkswagen - Wikipedia
            rating: 3
            tags:
              - car
              - volkswagen
              - germany
            url: https://en.wikipedia.org/wiki/Volkswagen
            kind: web-article

        Note without this yaml file the content will be passed over and not imported into devonthink.
    """
    # INITIALISATION

    def __init__(
            self,
            log,
            importFolder,
            pathToDevonthinkDB,
            settings=False
    ):
        self.log = log
        log.debug("instansiating a new 'devonthink' object")
        self.settings = settings
        self.importFolder = importFolder
        self.pathToDevonthinkDB = pathToDevonthinkDB
        # xt-self-arg-tmpx

        return None

    def ingest(self):
        """
        *import all of the media content found in the import folder into devonthink*

        **Return:**
            - ``None``

        **Usage:**

            To import the content into devonthink use:

            .. code-block:: python

                dtDB.ingest()

            This will import the media into the media-kind group in the devonthink database given:

            .. image:: https://i.imgur.com/FlWsqwQ.png
                :width: 800px

            Add metadata field are populated including tags, rating (as devonthink label) and the URL field if given in the yaml metadata. Note for tagging to work you will have to install `jdberry's 'tag' <https://github.com/jdberry/tag>`_ (a command line tool to manipulate tags on Mac OS X files, and to query for files with those tags.)
        """
        self.log.info('starting the ``ingest`` method')

        basePath = self.importFolder
        for mediaKind in os.listdir(basePath):
            mediaKindPath = os.path.join(basePath, mediaKind)
            if os.path.isdir(mediaKindPath):
                for mediaTitle in os.listdir(mediaKindPath):
                    mediaContainer = os.path.join(mediaKindPath, mediaTitle)
                    if os.path.isdir(mediaContainer):
                        metadata = self._media_metadata(
                            mediaTitle=mediaTitle,
                            mediaKind=mediaKind,
                            mediaContainer=mediaContainer
                        )

                        if not metadata:
                            continue

                        self._tag_media(
                            metadata=metadata,
                            mediaContainer=mediaContainer
                        )

                        self._import_media_to_devonthink(
                            metadata=metadata,
                            mediaContainer=mediaContainer
                        )

        self.log.info('completed the ``ingest`` method')
        return None

    def _media_metadata(
            self,
            mediaTitle,
            mediaKind,
            mediaContainer):
        """*media metadata*

        **Key Arguments:**
            - ``mediaTitle`` -- the title of the media as set by the containing folder name
            - ``mediaKind`` -- the kind of media as set by the name of the parent folder of the container
            - ``mediaContainer`` -- the path to the contain of the media

        **Return:**
            - ``metadata`` -- a dictionary of the media's metadata
        """
        self.log.info('starting the ``_media_metadata`` method')

        yamlFound = False
        basePath = mediaContainer
        for d in os.listdir(basePath):
            if os.path.isfile(os.path.join(basePath, d)) and ".yaml" in d:
                yamlFound = True
                stream = file(os.path.join(basePath, d), 'r')
                metadata = yaml.load(stream)
                stream.close()

        if not yamlFound:
            return None

        metadata["title"] = mediaTitle
        metadata["kind"] = mediaKind

        self.log.info('completed the ``_media_metadata`` method')
        return metadata

    def _tag_media(
            self,
            metadata,
            mediaContainer):
        """*tag the media in the container*

        **Key Arguments:**
            - ``metadata`` -- a dictionary of the media's metadata
            - ``mediaContainer`` -- the path to the contain of the media

        **Return:**
            - None
        """
        self.log.info('starting the ``_tag_media`` method')

        tagString = ", ".join(metadata["tags"])

        sys.path.append("/usr/local/bin")

        # TAG THE ITEMS
        if len(tagString):

            cmd = u"""export PATH="/usr/local/bin:$PATH" && tag -a "%(tagString)s" "%(mediaContainer)s" """ % locals(
            )
            p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
            stdout, stderr = p.communicate()
            self.log.debug('output: %(stdout)s' % locals())

        self.log.info('completed the ``_tag_media`` method')
        return None

    def _import_media_to_devonthink(
            self,
            metadata,
            mediaContainer):
        """*import media to devonthink and assign metadata values in the appropriate fields*

        **Key Arguments:**
            - ``metadata`` -- a dictionary of the media's metadata
            - ``mediaContainer`` -- the path to the contain of the media

        **Return:**
            - None
        """
        self.log.info('starting the ``_import_media_to_devonthink`` method')

        # RUN APPLESCIPT FROM THE PYTHON
        dtDB = os.path.basename(
            self.pathToDevonthinkDB).replace(".dtBase2", "")
        dtDBPath = self.pathToDevonthinkDB
        exists = os.path.exists(dtDBPath)
        if not exists:
            print "The devonthink database does not exits at %(dtDBPath)s" % locals()

        stars = int(metadata["rating"])
        url = metadata["url"]
        dtLabel = 6 - stars
        kind = metadata["kind"]

        applescript = """
            tell application id "DNtp"
                set toPath to "%(kind)s"
                set databasePath to "%(dtDBPath)s"
                set toDatabase to (POSIX path of databasePath)
                set toDatabase to open database toDatabase
                set theDestination to create location toPath in toDatabase
                set dtRecord to import "%(mediaContainer)s" to theDestination
                set url of dtRecord to "%(url)s"
                set exclude from tagging of dtRecord to true
                set label of dtRecord to %(dtLabel)s
                set kids to children of dtRecord
                repeat with k in kids
                    set label of k to %(dtLabel)s
                    set url of k to "%(url)s"
                end repeat
                set dtUrl to reference url of dtRecord
                return dtUrl
            end tell
""" % locals()

        self.log.debug('devonthink applescript: %(applescript)s' % locals())
        cmd = "\n".join(["osascript << EOT", applescript, "EOT"])
        p = Popen(cmd, stdout=PIPE, stdin=PIPE, shell=True)
        output = p.communicate()[0]
        self.log.debug('output: %(output)s' % locals())

        # GET THE DEVONTHINK URL OF THE FOLDER
        matchObject = re.finditer(
            r'x-devonthink-item.*',
            output,
            flags=0  # re.S
        )

        if matchObject == None:
            log.error(
                'cound not archive to devonthink: `%(output)s`' % locals())
        else:
            for m in matchObject:
                webbrowser.open_new_tab(m.group(0))
            # DELETE CONTAINER
            try:
                shutil.rmtree(mediaContainer)
            except:
                pass

        self.log.info('completed the ``_import_media_to_devonthink`` method')
        return None

    # use the tab-trigger below for new method
    # xt-class-method
