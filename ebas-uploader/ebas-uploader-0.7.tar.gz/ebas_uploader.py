#!/usr/bin/env python

# Example for uploading with start- and end-times
# ebas-uploader --watch-path=./data --archive-path=./archive --error-path=./errors --config=ebas-uploader-config.json --start-time=20:00 --end-time=5:00

import os
import time
import json
import Queue

import click
import datetime
import requests
import subprocess

from dateutil.parser import parse
from opbeat import Client
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

MAX_BACKOFF = 300

"""
Optionally include a file called exclude.py or hr_exclude.py
in which you can save a tuple/list of strings to look for
when removing lines before uploading (example content below)

EXCLUDE = (
    'PRINT GROUP BASED REPORT',
    'A REPORT WITH PATIENT DATA ACCESSED'
)
"""

try:
    from exclude import EXCLUDE
except ImportError:
    EXCLUDE = None

try:
    from hr_exclude import HR_EXCLUDE
except ImportError:
    HR_EXCLUDE = None


class EBAPostEventHandler(FileSystemEventHandler):

    ARCHIVE_MAGIC_NAME = " - Archive"
    errors = Queue.Queue()

    def __init__(self, archive_path, archive_length, error_path, config, silent, start_time, end_time, hr_data):
        self.archive_path = archive_path
        self.archive_length = archive_length
        self.error_path = error_path
        self.config = config

        if silent:
            self.opbeat_client = Client()
        else:
            self.opbeat_client = Client(
                organization_id='ef2e42e717494d91b3e7ed69c46d0415',
                app_id='3762432b73',
                secret_token='f13fd6f6e9b6998053adcb94409de0844ce80f4b',
            )

        self.start_time = self.end_time = None

        if start_time and end_time:
            self.start_time = start_time
            self.end_time = end_time

        if hr_data:
            self.exclude = HR_EXCLUDE
        else:
            self.exclude = EXCLUDE

    def upload_file(self, src_path, upload_file):
        config = self.config
        url = config["url"]

        if os.path.getsize(src_path) == 0:
            click.echo('Archiving empty file and skipping upload')
            return

        click.echo("Uploading to: {}".format(url))

        try:
            r = requests.post(
                url,
                data={
                    "key": config["key"],
                    "user": config["user"],
                    "delimiter": config["delimiter"],
                    "bulk_format": config["bulk_format"],
                    "upload_type": config["upload_type"],
                    "organization": config["organization"],
                },
                files={"upload_file": open(upload_file, "rb")}
            )

            click.echo("Uploaded {}".format(upload_file))
            click.echo("{} {}".format(r.status_code, r.reason))

        except Exception as e:
            message = "Upload of {} failed".format(upload_file) + ". Error: %s" % e
            self.errors.put(message)
            self.opbeat_client.captureMessage(message)

    def archive_file(self, src_file):
        try:
            os.rename(
                src_file,
                os.path.join(self.archive_path, os.path.basename(src_file))
            )
            click.echo("Archived {}".format(src_file))
        except Exception as e:
            click.echo("Did not archive {}".format(src_file) + ". Error: %s" % e)
            if os.path.exists(src_file):
                try:
                    os.rename(src_file, src_file + self.ARCHIVE_MAGIC_NAME)
                except Exception as e:
                    message = "Could not rename {}".format(src_file) + ". Error: %s" % e
                    click.echo(message)
                    self.opbeat_client.captureMessage(message)

        if self.archive_length > 0:
            self.delete_old_archive_files()

    def delete_old_archive_files(self):
        files = [f for f in os.listdir(self.archive_path) if os.path.isfile(os.path.join(self.archive_path, f))]
        click.echo("Scanning archive files")
        for f in files:
            st = os.stat(os.path.join(self.archive_path, f))
            age_in_days = (datetime.datetime.now() - datetime.datetime.fromtimestamp(st.st_mtime)).days
            if age_in_days >= self.archive_length:
                os.remove(os.path.join(self.archive_path, f))
                click.echo("Deleted file {}".format(f))

    def dispatch(self, event):
        if event.is_directory:
            return
        return super(EBAPostEventHandler, self).dispatch(event)

    def detect_file_modification(self, path, backoff_period=None):
        previous_change = os.stat(path).st_ctime
        backoff_period = backoff(backoff_period)
        current_change = os.stat(path).st_ctime

        # check that the file has not been modified since the last status change
        if current_change > previous_change:
            click.echo("Detected file modification for {}".format(path))
            click.echo("Re-checking modification in {} seconds".format(backoff_period))

            self.detect_file_modification(path, backoff_period)
        else:
            click.echo("No further file modification detected")

    def on_created(self, event):
        self.check_upload_time_range()
        self.process_file(event.src_path)

    def process_file(self, src_path):
        if self.ARCHIVE_MAGIC_NAME not in src_path:
            self.detect_file_modification(src_path)
            self.parse_rows(src_path)
            self.archive_file(src_path)

    def reprocess_existing_files(self, watch_path):
        for file_name in os.listdir(watch_path):
            self.process_file(watch_path + "/" + file_name)

    # parses rows in input to remove non-utf-8 characters
    def parse_rows(self, src_path):
        click.echo("Scanning file for unknown characters and eliminating excluded patterns")
        name = os.path.splitext(src_path)[0].split('/')[-1]

        path_to_accepted_file = os.path.join(self.archive_path, name + '_accepted.txt')
        path_to_errored_file = os.path.join(self.error_path, name + '_errored.txt')

        # passes once through the input file
        # if a row matches any non-utf8 characters it is outputted to an error file in error_path
        # otherwise the row is outputted to an accepted file in archive_path

        remove = ''
        if self.exclude:
            for val in self.exclude:
                remove += ' || /%s/' % val

        cmd = r'/[\x80-\xFF]/' + remove + ' {print $0 > "' + path_to_errored_file + '"; next}{print $0 > "' + path_to_accepted_file + '"}'
        subprocess.call(['awk', cmd, src_path])

        # upload the accepted rows
        self.upload_file(src_path, path_to_accepted_file)

    def check_upload_time_range(self):
        '''
        If start- and end-time arguments are provided on program start,
        this function will execute as new uploads arrive
        and will ensure uploads occur only during the specified range.

        Start- and end-time arguments are strings, formatted 0:00 - 23:59.
        '''
        if self.start_time:
            start = parse(self.start_time)
            end = parse(self.end_time)
            now = datetime.datetime.now()

            day = start < end
            night = start > end

            # If uploads are set to start overnight,
            # the current time should be >= the start-time OR < the end-time
            # on a given calendar day
            if night and (now >= start or now < end):
                pass
            # If uploads are set to occur during the day,
            # the current time should be >= the start-time AND < the end-time
            # on a given calendar day
            elif day and (now >= start and now < end):
                pass
            else:
                # If uploads are set to occur during the day
                # and a file for upload has arrived after the set end-time,
                # the start-time should be pushed to the next day
                if day and now > end:
                    start = start + datetime.timedelta(days=1)
                diff = int((start - now).total_seconds())
                click.echo('Uploading is paused until {0}'.format(start))
                time.sleep(diff)


@click.command()
@click.option("--watch-path", type=click.Path(), required=True, help="path to watch")
@click.option("--archive-path", type=click.Path(), required=True, help="path to archive files to")
@click.option("--archive-length", type=int, default=0, help="number of days after upload before deleting archived file")
@click.option("--error-path", required=True, help="path to put file of errored rows")
@click.option("--config", type=click.File(), required=True, help="JSON config file downloaded from EBAS")
@click.option("--silent", is_flag=True, required=False, help="Set this flag to not report errors to Maize")
@click.option("--start-time", required=False, help="Set this flag along with --end-time to ensure uploads are only started in a specific time range (format 0:00-23:59)")
@click.option("--end-time", required=False, help="Set this flag along with --start-time to ensure uploads are only started in a specific time range (format 0:00-23:59)")
@click.option("--hr-data", required=False, is_flag=True, help="Include this flag to specify that an HR data file is being uploaded, and the HR exclude strings should be used")
@click.version_option()
def main(watch_path, archive_path, archive_length, error_path, config, silent, start_time, end_time, hr_data):
    """
    watches a folder and auto-uploads files to an EBAS node with the given
    configuration for processing
    """
    config_data = json.load(config)
    event_handler = EBAPostEventHandler(archive_path, archive_length, error_path, config_data, silent, start_time, end_time, hr_data)
    stop = False
    backoff_period = 1
    observer = None

    while not stop:
        try:
            error = None

            event_handler.reprocess_existing_files(watch_path)

            observer = Observer()
            observer.schedule(event_handler, watch_path, recursive=False)
            observer.start()

            while not error:
                try:
                    error = event_handler.errors.get(block=False)
                    backoff_period = restart(observer, error, backoff_period)
                except Queue.Empty:
                    time.sleep(1)
                    backoff_period = 1
        except KeyboardInterrupt:
            if observer:
                observer.stop()
                observer.join()

            stop = True
        except Exception as e:
            backoff_period = restart(observer, e, backoff_period)


def restart(observer, e, backoff_period):
    if observer:
        observer.stop()
        observer.join()

    click.echo("Error: %s" % e)
    click.echo("Retrying uploads in {} seconds".format(backoff_period))
    backoff_period = backoff(backoff_period)

    return backoff_period


def backoff(backoff_period=None):
    if backoff_period is None:
        backoff_period = 1

    # wait
    time.sleep(backoff_period)

    backoff_period *= 2

    if backoff_period > MAX_BACKOFF:
        backoff_period = MAX_BACKOFF

    return backoff_period

if __name__ == "__main__":
    main()
