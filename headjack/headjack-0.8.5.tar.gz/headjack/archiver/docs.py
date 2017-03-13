#!/usr/local/bin/python
# encoding: utf-8
"""
*archive various document formats to Papers.app on macOS, alongside assicated metadata given in markdown notes file*

:Author:
    David Young

:Date Created:
    October 22, 2016
"""
################# GLOBAL IMPORTS ####################
import sys
import os
import codecs
import re
import markdown as md
os.environ['TERM'] = 'vt100'
from fundamentals import tools
from fundamentals.mysql import writequery
from subprocess import Popen, PIPE, STDOUT


def handler(e):
    return (u' ', e.start + 1)
codecs.register_error('dryx', handler)


class docs():
    """
    *archive various document formats to Papers.app on macOS, alongside assicated metadata given in markdown notes file*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary
        - ``dbConn`` -- the database connection
    """
    # Initialisation

    def __init__(
            self,
            log,
            dbConn,
            settings=False,

    ):
        self.log = log
        self.log.debug("instansiating a new 'docs' object")
        self.settings = settings
        self.dbConn = dbConn
        # xt-self-arg-tmpx

        # CREATE APPLESCRIPT RETURN STRING REQUIRED BY PAPERS APP
        self.asProperties = {
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
        self.returnString = "return "
        for i, v in enumerate(self.asProperties.values()):
            if i + 1 == len(self.asProperties):
                self.returnString += """ %(v)s of thisItem""" % locals()
            else:
                self.returnString += """ %(v)s of thisItem & "||" & """ % locals()

        return None

    def archive(
            self):
        """*archive the media content found in the stashed folder at the root of the media staging folder into Papers.app*

        The database entry for the item will also be updated with the notes, ratings and tag etc set within the associated notes file.

        **Return:**
            - None

        **Usage:**

            To archive media and notes in the media staging folder's stash run the following:

            .. code-block:: python 

                from headjack.archiver import docs
                stager = docs(
                    log=log,
                    settings=settings,
                    dbConn=dbConn
                )  
                stager.archive()

            This will import the media into Papers.app, update the metadata in Papers.app to match that found in the associated notes file, update the relevant database table and then move the media and note files into a `trash` folder at the root of the media staging folder.
        """
        self.log.info('starting the ``archive`` method')

        # ARCHIVED STAGED ENTRIES
        mediaStagingFolder = self.settings[
            "workflow_folders"]["media_staging_folder"] + "/stashed"
        docs, meta, mdNotes, mdContent = self._collect_docs_with_metadata(
            mediaStagingFolder=mediaStagingFolder
        )
        for d, m, n, c in zip(docs, meta, mdNotes, mdContent):
            self._archive_to_papers_app(
                meta=m,
                mediaPath=d,
                markdownPath=n,
                notes=c,
                mediaStagingFolder=mediaStagingFolder
            )

        self.log.info('completed the ``archive`` method')
        return None

    def stash(self):
        """
        *stash media content ready to be archived*

        **Return:**
            - None

        **Usage:**

            To 'stash' media and notes in the media staging folder (found in the settings file) run the following:

            .. code-block:: python 

                from headjack.archiver import docs
                stager = docs(
                    log=log,
                    settings=settings,
                    dbConn=dbConn
                )  
                stager.stash()

            This will delete media that is flagged for removal in the frontmatter of the associated MD notes file (`action: delete`) and move media items that are flagged for archival (`action: archive`) into a stashed folder at the root of the media staging folder
        """
        self.log.info('starting the ``archive`` method')
        mediaStagingFolder = self.settings[
            "workflow_folders"]["media_staging_folder"]
        docs, meta, mdNotes, mdContent = self._collect_docs_with_metadata(
            mediaStagingFolder=mediaStagingFolder
        )

        # DELETE / STASH ENTRIES
        for d, m, n in zip(docs, meta, mdNotes):
            if "action" in m and m["action"] == "delete":
                self._delete_media(
                    meta=m,
                    mediaPath=d,
                    markdownPath=n,
                    mediaStagingFolder=mediaStagingFolder
                )
            if "action" in m and m["action"] == "archive":
                if len(m["tags"]) == 0:
                    print "%(n)s needs tags added" % locals()
                    continue
                self._stash_media(
                    meta=m,
                    mediaPath=d,
                    markdownPath=n,
                    mediaStagingFolder=mediaStagingFolder
                )

        self.log.info('completed the ``archive`` method')
        return None

    def _parse_associated_notes_file(
            self,
            markdownFilepath):
        """*parse a media file's associated note file to extract the markdown notes and the frontmatter metadata*

        **Key Arguments:**
            - ``markdownFilepath`` -- the path to the associated markdown file

        **Return:**
            - ``docMetadata`` -- the metadata found in the associated markdown file (python dictionary)
            - ``mdContent`` -- the content of the MD file
        """
        self.log.info('starting the ``_parse_associated_notes_file`` method')

        # READ THE FILE DATA
        pathToReadFile = markdownFilepath
        self.log.debug('reading file %(markdownFilepath)s' % locals())
        try:
            self.log.debug(
                "attempting to open the file %s" % (pathToReadFile,))
            readFile = codecs.open(
                pathToReadFile, encoding='utf-8', mode='r')
            thisData = readFile.read()
            readFile.close()
        except IOError, e:
            message = 'could not open the file %s' % (pathToReadFile,)
            self.log.critical(message)
            raise IOError(message)
        readFile.close()

        # CLEAN THE HEADER SO MD PACKAGE CAN READ METADATA
        matchObject = re.search(r"^(.*)\n\n", thisData, re.S)
        if matchObject:
            header = matchObject.group(1)
            r1 = re.compile(r'(.*)\: *\n')
            header = r1.sub("\g<1>: null\n", header)
            thisData = thisData.replace(matchObject.group(1), header)

        # PARSE CONTENT TO GRAB METADATA
        mdParser = md.Markdown(
            extensions=['meta'])
        html = mdParser.convert(thisData)
        if not hasattr(mdParser, 'Meta'):
            self.log.debug(
                'no metadata found in %(f)s, moving on' % locals())
            return None
        metadata = mdParser.Meta

        # CLEAN UP QUOTES
        if len(metadata):
            thisData = re.search(r"\n\n+(.*)$", thisData, re.S)
            thisData = thisData.group(1).strip().replace(
                '"', '\\"')
        newMeta = dict(metadata)
        for k, v in metadata.iteritems():
            newMeta[k] = v[0].replace(
                '"', '\\"')
        inputMetadata = newMeta

        self.log.info('completed the ``_parse_associated_notes_file`` method')
        return inputMetadata, thisData

    def _collect_docs_with_metadata(
            self,
            mediaStagingFolder):
        """*give the path to the media staging folder, collect all of the media files and there associated notes and metadata into a collection of lists (indices synced)*

        **Key Arguments:**
            - ``mediaStagingFolder`` -- path to the folder containing the media for notes staged for archive/deletion

        **Return:**
            - ``docs`` -- a list to the document file paths
            - ``meta`` -- a list of metadata dictionaries (same len as docs)
            - ``mdNotes`` -- the paths to the MD notes files.
            - ``mdContent`` -- the note content of the MD notes files
        """
        self.log.info('starting the ``_collect_docs_with_metadata`` method')

        docs = []
        meta = []
        mdNotes = []
        mdContent = []

        basePath = mediaStagingFolder
        for f in os.listdir(basePath):
            if os.path.isfile(os.path.join(basePath, f)) and f.split(".")[-1] == "md":
                markdownFilepath = os.path.join(mediaStagingFolder, f)
                mdNotes.append(markdownFilepath)

                docMetadata, noteContent = self._parse_associated_notes_file(
                    markdownFilepath=markdownFilepath
                )
                meta.append(docMetadata)

                if "pdfname" in docMetadata:
                    mediaName = docMetadata["pdfname"]
                elif "podcastName" in docMetadata:
                    mediaName = docMetadata["podcastName"]
                elif "videoName" in docMetadata:
                    mediaName = docMetadata["videoName"]
                else:
                    mediaName = None

                if mediaName:
                    mediaName = os.path.join(
                        mediaStagingFolder, mediaName)

                docs.append(mediaName)
                mdContent.append(noteContent)

        self.log.info('completed the ``_collect_docs_with_metadata`` method')
        return docs, meta, mdNotes, mdContent

    def _delete_media(
            self,
            meta,
            mediaPath,
            markdownPath,
            mediaStagingFolder):
        """*Delete media from filesystem and flag in database as deleted*

        **Key Arguments:**
            - ``meta`` -- the metadata for the given media file.
            - ``mediaPath`` -- path to the media file
            - ``markdownPath`` -- path to the markdown notes file
            - ``mediaStagingFolder`` -- path to the folder containing the media for notes staged for archive/deletion
        """
        self.log.info('starting the ``_delete_media`` method')

        if "databaseid" in meta:
            databaseid = meta["databaseid"]
            if databaseid and databaseid.lower() != "false":
                sqlQuery = u"""
                    update `reading-list` set workflowStage = "deleted" where primaryId = %(databaseid)s 
                """ % locals()
                writequery(
                    log=self.log,
                    sqlQuery=sqlQuery,
                    dbConn=self.dbConn,
                )
        # Recursively create missing directories
        if not os.path.exists(mediaStagingFolder + "/trash"):
            os.makedirs(mediaStagingFolder + "/trash")
        if mediaPath:
            source = mediaPath
            destination = ("/").join(mediaPath.split("/")
                                     [0:-1]) + "/trash/" + mediaPath.split("/")[-1]
            self.log.debug("attempting to rename file %s to %s" %
                           (source, destination))
            os.rename(source, destination)

        try:
            source = markdownPath
            destination = ("/").join(markdownPath.split("/")
                                     [0:-1]) + "/trash/" + markdownPath.split("/")[-1]
            self.log.debug("attempting to rename file %s to %s" %
                           (source, destination))
            os.rename(source, destination)
        except Exception, e:
            self.log.error("could not rename file %s to %s - failed with this error: %s " %
                           (source, destination, str(e),))
            sys.exit(0)

        self.log.info('completed the ``_delete_media`` method')
        return None

    def _stash_media(
            self,
            meta,
            mediaPath,
            markdownPath,
            mediaStagingFolder):
        """*stash media in a 'stashed' folder at the root of the media staging folder*

        **Key Arguments:**
            - ``meta`` -- the metadata for the given media file.
            - ``mediaPath`` -- path to the media file
            - ``markdownPath`` -- path to the markdown notes file
            - ``mediaStagingFolder`` -- path to the folder containing the media for notes staged for archive/deletion
        """
        self.log.info('starting the ``_stash_media`` method')

        # Recursively create missing directories
        if not os.path.exists(mediaStagingFolder + "/stashed"):
            os.makedirs(mediaStagingFolder + "/stashed")
        if mediaPath:
            source = mediaPath
            destination = ("/").join(mediaPath.split("/")
                                     [0:-1]) + "/stashed/" + mediaPath.split("/")[-1]
            self.log.debug("attempting to rename file %s to %s" %
                           (source, destination))
            os.rename(source, destination)

        try:
            source = markdownPath
            destination = ("/").join(markdownPath.split("/")
                                     [0:-1]) + "/stashed/" + markdownPath.split("/")[-1]
            self.log.debug("attempting to rename file %s to %s" %
                           (source, destination))
            os.rename(source, destination)
        except Exception, e:
            self.log.error("could not rename file %s to %s - failed with this error: %s " %
                           (source, destination, str(e),))
            sys.exit(0)

        self.log.info('completed the ``_stash_media`` method')
        return None

    def _archive_to_papers_app(
            self,
            meta,
            mediaPath,
            notes,
            markdownPath,
            mediaStagingFolder):
        """*archive media to the macOS Papers.app*

        **Key Arguments:**
            - ``meta`` -- the metadata for the given media file.
            - ``mediaPath`` -- path to the media file
            - ``notes`` -- the text content of the note file
            - ``markdownPath`` -- path to the markdown notes file
            - ``mediaStagingFolder`` -- path to the folder containing the media for notes staged for archive/deletion

        **Return:**
            - ``None``
        """
        self.log.info('starting the ``_archive_to_papers_app`` method')

        outputMetadata = self._import_media_and_return_metadata(
            log=self.log,
            mediaPath=mediaPath
        )

        # CHECK FILE WAS INDEED IMPORTED
        if mediaPath and outputMetadata["originalPath"] != mediaPath:
            originalPath = outputMetadata["originalPath"]
            self.log.error(
                'this is not the original file: "%(originalPath)s" ' % locals())
            sys.exit(0)

        else:
            updates = ""
            sqlUpdates = ""
            sqlTags = ""
            if "databaseid" in meta:
                databaseid = meta["databaseid"]
            else:
                databaseid = None

            thisId = outputMetadata["papersId"]
            for k, v in meta.iteritems():
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
                    if k in self.asProperties:
                        prop = self.asProperties[k]
                        updates += """set %(prop)s of thisItem to "%(v)s"\n""" % locals()
                        if len(sqlUpdates):
                            sqlUpdates += """, %(k)s = "%(v)s" """ % locals(
                            )
                        else:
                            sqlUpdates += """update `reading-list`  set %(k)s = "%(v)s" """ % locals(
                            )

            if len(notes):
                import pyperclip
                pyperclip.copy(notes)

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
                return None
            elif "error" in output.lower():
                print output
                sys.exit(0)
            elif len(output) == 0:
                print "Error in applescript:\n"
                print applescript
                sys.exit(0)

            papersId = output
            if databaseid and databaseid.lower() != "false":
                sqlUpdates += """, papersId = "%(papersId)s", workflowStage = "archived", notes = "%(notes)s"  where primaryId = %(databaseid)s """ % locals()
                sqlUpdates = sqlUpdates.encode("utf8")
                writequery(
                    log=self.log,
                    sqlQuery=sqlUpdates,
                    dbConn=self.dbConn,
                )
                sqlTags = sqlTags.encode("utf8")
                writequery(
                    log=self.log,
                    sqlQuery=sqlTags,
                    dbConn=self.dbConn,
                )

            # Recursively create missing directories
            if not os.path.exists(mediaStagingFolder + "/../trash"):
                os.makedirs(mediaStagingFolder + "/../trash")
            if mediaPath:
                source = mediaPath
                destination = ("/").join(mediaPath.split("/")
                                         [0:-1]) + "/../trash/" + mediaPath.split("/")[-1]
                self.log.debug("attempting to rename file %s to %s" %
                               (source, destination))
                os.rename(source, destination)

            source = markdownPath
            destination = ("/").join(markdownPath.split("/")
                                     [0:-1]) + "/../trash/" + markdownPath.split("/")[-1]
            self.log.debug("attempting to rename file %s to %s" %
                           (source, destination))
            os.rename(source, destination)

        self.log.info('completed the ``_archive_to_papers_app`` method')
        return None

    def _import_media_and_return_metadata(
            self,
            log,
            mediaPath):
        """*import one media file into Papers.app and return the default metadata as set by Papers.app (to then be modified)*

        **Key Arguments:**
            - ``log`` -- logger
            - ``mediaPath`` -- the path to the media file to import.

        **Return:**
            - ``outputMetadata`` -- the metadata for the paper    
        """
        self.log.info(
            'starting the ``_import_media_and_return_metadata`` function')

        returnString = self.returnString

        if not mediaPath:
            moduleDirectory = os.path.dirname(__file__)
            mediaPath = moduleDirectory + "/resources/media-placeholder.png"

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
        for val, key in zip(output, self.asProperties.keys()):
            # RECODE INTO ASCII

            val = val.decode("utf-8")
            # val = val.encode("ascii", "dryx")
            outputMetadata[key] = val.replace(
                ", ", "").replace('"', '\"').replace("'", "\'")

        self.log.info(
            'completed the ``_import_media_and_return_metadata`` function')
        return outputMetadata

    # use the tab-trigger below for new method
    # xt-class-method
