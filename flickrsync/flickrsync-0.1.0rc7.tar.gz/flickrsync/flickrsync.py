#!/usr/bin/python3
import argparse
import os
import sys
import multiprocessing
import logging
import traceback
import datetime

from flickrsync import general
from flickrsync import local
from flickrsync.settings import Settings
from flickrsync.database import Database
from flickrsync.flickr import Flickr
from flickrsync.error import Error
from flickrsync.log import Log

logger = logging.getLogger(Log.NAME)

COMMIT_SIZE = 50

def delete_tables(database, noprompt=False):
    if noprompt or general.query_yes_no('Delete the database?', default='no'):
        database.drop_local_photos_table()
        database.drop_flickr_photos_table()
        database.create_local_photos_table()
        database.create_flickr_photos_table()

def _commit_photos(database, photos):
    database.insert_local_photos(photos)
    database.do_commit()
    logger.info('Added <%d> new photos' % len(photos))

def _search_local(database, directory):
    allfiles = database.select_all_local_photos()
    deletedfiles = local.search_deleted(allfiles)

    if deletedfiles :
        database.update_deleted_photos(deletedfiles)
    else:
        logger.info('No deleted / undeleted photos found')

    newsearch = local.search_photos(directory)

    if newsearch:
        newfiles = database.get_new_files(newsearch)

        if newfiles :
            logger.info('New files found <%s>' % len(newfiles))

            with multiprocessing.Pool() as pool:

                # not able to use the sqlite.row_factory type with map
                # convert to tuple list
                it = pool.imap_unordered(local.image_worker, general.tuple_list_from_rows(newfiles))

                photos = []
                for photo in it:

                    photos.append(photo)

                    if len(photos) >= COMMIT_SIZE:
                        _commit_photos(database, photos)
                        photos.clear()

                _commit_photos(database, photos)
        else:
            logger.info('No new files found')

    else:
        logger.warning('No files found in this directory <%s>' % directory)

def _get_flickr_photosets(database, flickr):
    photosets = flickr.get_photosets()

    database.create_flickr_photosets_table()

    if photosets :
        database.insert_flickr_photosets(photosets)

    else:
        logger.info('No flickr photoSets found')

    return photosets

def create_photosets(database, flickr, rootpath, noprompt=False):
    photosets = _get_flickr_photosets(database, flickr)
    directories = database.get_directories_from_local()

    if len(directories):
        if noprompt or general.query_yes_no('Potentially create / delete <%s> photosets on Flickr?' % len(directories)):
            photosetsused = []

            for directory in directories:
                photos = general.list_from_rows(database.select_flickr_photos_matching_local_by_directory(directory))

                if photos:
                    photosetname = general.get_photoset_name(directory, rootpath)
                    photoscsv = general.list_to_csv(photos)

                    primaryphotoid = photos[0]
                    photosetid = database.get_photoset_id(photosetname)

                    if photosetid:
                        logger.info('Photoset already exists on Flickr <%s>' % photosetname)
                    else:
                        photosetid = flickr.photoset_create(photosetname, primaryphotoid)

                    assert(photosetid), 'photosetId is Null'

                    # replace photos in set
                    flickr.photoset_edit(photosetid, primaryphotoid, photoscsv)
                    photosetsused.append(str(photosetid))

                else:
                    logger.warning('No photos found on Flickr match local photos found in <%s>' % directory)

            if photosetsused:
                flickr.delete_unused_photosets(photosetsused = photosetsused, photosets = photosets)
            else:
                logger.warning('no photosets in use')
    else:
        logger.info('No local photo directories found')

def _search_flickr(database, flickr, rebase=False):
    lastuploaddate = 0 if rebase else database.select_last_upload_date()
    photos = flickr.get_photos(lastuploaddate + 1)

    if photos :
        logger.info('Found new photos on Flickr <%d>' % len(photos))
        database.insert_flickr_photos(photos)
    else:
        humandate = datetime.datetime.fromtimestamp(lastuploaddate).strftime('%Y-%m-%d %H:%M:%S')
        logger.info('No new photos found on Flickr since the last upload date <%s>' % humandate)

def rebase_flickr(database, flickr, noprompt=False):
    if noprompt or general.query_yes_no('Rebase the Flickr database?', default='no'):
        database.drop_flickr_photos_table()
        database.create_flickr_photos_table()
        _search_flickr(database, flickr, rebase=True)

def _do_upload(database, flickr, directory, dryrun=True, noprompt=False):
    uploadphotos = database.select_photos_for_upload()

    logger.info('Selected <%d> photos for upload to Flickr' % len(uploadphotos))

    passed = 0
    failed = 0

    if dryrun:
        logger.info('Dry run, not uploading')
    else:
        if uploadphotos:
            if noprompt or general.query_yes_no('Upload <%d> pictures to Flickr?' % len(uploadphotos)):
                passed, failed = flickr.upload_photos(uploadphotos)
        else:
            logger.info('No photos to upload')

    logger.info('Uploaded: passed<%d>, failed<%d>' % (passed, failed))
    return passed

def _download_missing_photos_from_flickr(database, directory, dryrun=True, noprompt=False):

    flickrphotos = database.select_missing_flickr_photos()

    if flickrphotos:
        if noprompt or general.query_yes_no('Do you want to download <%d> missing photos from Flickr' % len(flickrphotos)):
            local.download_photos(directory=directory, flickrphotos=flickrphotos, dryrun=dryrun)
            _search_local(database, directory)
    else:
        logger.info('No missing photos to download')

def _add_tags(flickr, localphotos, dryrun=True):
    logger.info('Adding tags to <{count}> Flickr photos'.format(count=len(localphotos)))

    if dryrun:
        logger.info('Dry run, not adding tags')
    else:
        data = []

        for localphoto in localphotos:
            data.append((localphoto['flickrid'], flickr.get_signature_tag(localphoto['signature'])))

        for id, signature in data:
            flickr.add_tags(id, signature)

def _download_and_scan_unmatchable_flickr_photos(database, flickr, directory, dryrun=True, noprompt=False, nodatematch=False):
    flickrphotos = database.select_unmatchable_flickr_photos(nodatematch)

    if flickrphotos:
        if noprompt or general.query_yes_no('Do you want to download and scan <%d> unmatchable pictures from Flickr' % len(flickrphotos)):
            local.download_photos(directory=directory, flickrphotos=flickrphotos, dryrun=dryrun)
            _search_local(database, directory)

            localphotos = database.select_unmatched_photos_with_flickr_id()

            if localphotos:
                try:
                    _add_tags(flickr, localphotos, dryrun=dryrun)

                finally:
                    _search_flickr(database, flickr, rebase=True)
    else:
        logger.info('No unmatchable Flickr photos found')

def do_sync(database, flickr, directory, twoway=False, dryrun=True, noprompt=False, nodatematch=False):
    if noprompt or general.query_yes_no('Do you want to sync the local file system with Flickr'):
        procs = []

        proc = multiprocessing.Process(target = _search_local(database, directory), args = ())
        procs.append(proc)
        proc.start()

        proc = multiprocessing.Process(target = _search_flickr(database, flickr), args = ())
        procs.append(proc)
        proc.start()

        for proc in procs:
            proc.join(7200)  # only block for this amount of time
        database.do_commit()

        _download_and_scan_unmatchable_flickr_photos(database, flickr, directory, dryrun=dryrun, noprompt=noprompt, nodatematch=nodatematch)
        database.do_commit()

        uploaded_count = _do_upload(database, flickr, directory, dryrun=dryrun, noprompt=noprompt)

        if uploaded_count > 0:
            _search_flickr(database, flickr)

        if twoway:
            _download_missing_photos_from_flickr(database, directory, dryrun=dryrun, noprompt=noprompt)

def main():
    try:
        logger.debug('started')
        logger.debug("sys.argv<%s>" % str(sys.argv))

        parser = argparse.ArgumentParser(description = 'A command line tool to backup local file system pictures to Flickr')

        parser.add_argument("-c", "--config", type = str, help = "config file location")
        parser.add_argument("-p", "--profile", type = str, help = "config profile section")

        parser.add_argument("-u", "--username", type = str, help = "config Flickr username, overrides the config file")
        parser.add_argument("-d", "--database", type = str, help = "FlickrSync database location, overrides the config file")
        parser.add_argument("-l", "--directory", type = str, help = "local picture directory, overrides the config file")

        parser.add_argument("--auth", help = "authenticate with Flickr", action = "store_true")
        parser.add_argument("--sync", help = "perform a one way sync from the local file system to Flickr", action = "store_true")
        parser.add_argument("--sync2", help = "perform a two way sync between the local file system and Flickr", action = "store_true")
        parser.add_argument("--photosets", help = "create Flickr photosets based upon the local file system", action = "store_true")
        parser.add_argument("--delete", help = "delete the database tables", action = "store_true")
        parser.add_argument("--rebase", help = "rebase the Flickr database table", action = "store_true")
        parser.add_argument("--nodatematch", help = "do not use dates to match during the scanning phase", action = "store_true")
        parser.add_argument("--debug", help = "enable debug logging", action = "store_true")
        parser.add_argument("--dryrun", help = "do not actually upload/download, perform a dry run", action = "store_true")
        parser.add_argument("--noprompt", help = "do not prompt", action = "store_true")

        args = parser.parse_args()

        if args.debug:
            Log.set_level(logging.DEBUG)
        else:
            Log.set_level(logging.INFO)

        settings = Settings(args)

        if len(sys.argv) < 2:
            parser.print_usage()
            print()
            print('Config file location <%s>' % settings.configname)
            sys.exit(0)

        database = Database(settings.database)
        flickr = Flickr(settings.api_key, settings.api_secret, settings.username)

        if args.auth:
            flickr.authenticate()

        if args.delete:
            delete_tables(database, noprompt=args.noprompt)

        elif args.rebase:
            rebase_flickr(database, flickr, noprompt=args.noprompt)

        if args.sync:
            do_sync(database, flickr, settings.directory, twoway=False, dryrun=args.dryrun, noprompt=args.noprompt, nodatematch=args.nodatematch)

        elif args.sync2:
            do_sync(database, flickr, settings.directory, twoway=True, dryrun=args.dryrun, noprompt=args.noprompt, nodatematch=args.nodatematch)

        if args.photosets:
            create_photosets(database, flickr, settings.directory, noprompt=args.noprompt)

        database.con.close()

    except AssertionError as e:
        msg = 'AssertionError: %s' % e
        logger.error(msg)

    except Exception as e:
        Log.traceback(logger, e)
        logger.error(e)

    finally:
        logger.debug('finished')

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        msg = 'Last Error: %s' % e
        print(msg)
