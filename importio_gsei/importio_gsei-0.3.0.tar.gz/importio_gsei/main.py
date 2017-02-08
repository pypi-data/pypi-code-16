#
# Copyright 2016 Import.io
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import argparse
from importio_gsei.version import __version__
from importio_gsei import GoogleSheet
from importio_gsei import ExtractorGetUrlList
from importio_gsei import ExtractorPutUrlList
from importio_gsei import ExtractorStart
from importio_gsei import ExtractorStatus
import logging
import sys

CMD_COPY_URLS = 'copy-urls'
CMD_EXTRACT = 'extract'
CMD_EXTRACTOR_START = 'extractor-start'
CMD_EXTRACTOR_STATUS = 'extractor-status'
CMD_EXTRACTOR_URLS = 'extractor-urls'
CMD_SHEET_URLS = 'sheet-urls'

DESCRIPTION = "Import.io Google Sheets Extractor Integration"

logger = logging.getLogger(__name__)


class GsExtractorUrls(object):
    """
    Implements command line utility and API:

    1. Extract the target URLs from a Google Spreadsheet
    2. Add the extracted URLs to the Extractor
    3. Execute the Extractor

    Programmatic access to the commands are available, with an example shown here:

    from importio_gsei import GsUrlFeed

    g = GsExtractorUrls()
    g.extractor_start(extractor_id)

    """

    def __init__(self):
        """
        Initializes a NewsDriver instance
        """
        self._version = __version__
        self._debug = False
        self._command = None
        self._extractor_id = None
        self._spread_sheet_id = None
        self._spread_sheet_range = None

    def copy_urls(self, spread_sheet_id, spread_sheet_range, extractor_id):
        """
        Copies URLs from a Google sheet to an Extractor
        :param spread_sheet_id: Google Sheet Identifier
        :param spread_sheet_range: Absolute or relative spread sheet range that locates the URLs on the sheet
        :param extractor_id: Identifies the target Extractor to copy URLs to
        :return: None
        """
        logger.info("Copy URLs from Google Sheet: {0} from range: {1} to Extractor: {2}".format(
            spread_sheet_id, spread_sheet_range, extractor_id))
        sheet = GoogleSheet(spreadsheet_id=spread_sheet_id, range=spread_sheet_range)
        sheet.initialize_service()
        urls = sheet.get_urls()
        logger.debug("sheet-urls ({0}): {1}".format(type(urls), urls))
        extractor = ExtractorPutUrlList(extractor_id=extractor_id)
        extractor.put(urls)

    def extract(self, spread_sheet_id, spread_sheet_range, extractor_id):
        """
        Performs the entire copy of URLs from the Google sheet to Extractor and starts a craw run

        :param spread_sheet_id: Google sheet identifier
        :param spread_sheet_range: Absolute or relative spread sheet range that locates
        :param extractor_id: Identifies the Extractor to copy URLs to and execute
        :return: Status of the crawl run and GUID
        """
        logger.info("Pull URLs from Google Sheet: {0} from range: {1} to Extractor: {2} and run".format(
            spread_sheet_id, spread_sheet_range, extractor_id))
        self.copy_urls(spread_sheet_id, spread_sheet_range, extractor_id)
        return self.extractor_start(extractor_id)

    def extractor_start(self, extractor_id):
        """
        Starts a crawl run for an Extractor
        :param extractor_id: Identifies the extractor to start a craw run for
        :return: Status of the crawl run and GUID
        """
        logger.info("Starting crawl run for extractor: {0}".format(extractor_id))
        extractor = ExtractorStart(extractor_id=extractor_id)
        return extractor.start()

    def extractor_status(self, extractor_id):
        """
        Returns the crawl-run status for the specific extractor
        :param extractor_id: Identifies the extractor to get the crawl runs from
        :return: A list of crawl-run dictionaries that contains status information
        """
        logger.info("Status for extractor: {0}".format(extractor_id))
        extractor = ExtractorStatus(extractor_id=extractor_id)
        return extractor.get()

    def extractor_urls(self, extractor_id):
        """
        Returns list of URLs associated with a specific extractor
        :param extractor_id: Identifies the extractor to pull the URLs for
        :return: A list of strings contains URLs
        """
        logger.info("Display URLs from Extractor: {0}".format(extractor_id))
        api = ExtractorGetUrlList(extractor_id=extractor_id)
        return api.get()

    def sheet_urls(self, spread_sheet_id, spread_sheet_range):
        """
        Returns a list of URLs associated with a Google sheet and a specified range
        :param spread_sheet_id: Google Sheet identifier
        :param spread_sheet_range: Specific range that contains the URLs
        :return:
        """
        logger.info("Display URLs from Google Sheet: {0} from range: {1}".format(
            spread_sheet_id, spread_sheet_range))
        sheet = GoogleSheet(spreadsheet_id=spread_sheet_id, range=spread_sheet_range)
        sheet.initialize_service()
        return sheet.get_urls()

    def _add_extractor_id_argument(self, parser):
        """
        Add extractor id argument
        :param parser: Parser to add argument to
        :return: None
        """
        parser.add_argument('-e', '--extractor-id', metavar='extractor_id',
                            dest="extractor_id", action='store', required=True,
                            help='Import.io extractor id or GUID')

    def _add_debug_argument(self, parser):
        """
        Add a debug argument to a parser
        :param parser: Parser to add argument to
        :return:
        """
        parser.add_argument('-d', '--debug', dest="debug", action='store_true',
                            help="Enables debug logging")

    def _add_spread_sheet_id_argument(self, parser):
        """
        Add spread sheet id argument to a parser
        :param parser: Parser to add the argument to
        :return: None
        """
        parser.add_argument('-i', '--sheet-id', dest="spread_sheet_id", metavar='spread_sheet_id',
                            action='store', required=True,
                            help="Google spreadsheet identifier")

    def _add_range_argument(self, parser):
        """
        Add spread sheet range to a parser
        :param parser:
        :return: None
        """
        parser.add_argument('-r', '--range', dest="spread_sheet_range", metavar='spread_sheet_range',
                            action='store', required=False,
                            help="Range identifying the list of URLs")

    def _handle_arguments(self):
        """
        Processes the command line arguments for each of the sub-commands
        :return: None
        """

        logger.info("Process command line arguments")

        parser = argparse.ArgumentParser(description=DESCRIPTION)
        parser.add_argument('-v', '--version', action='version',
                            version='{version}'.format(version=__version__))
        subparser = parser.add_subparsers(help='commands')
        #
        # COPY URLS
        #
        copy_urls = subparser.add_parser(CMD_COPY_URLS, help='Copies URLs from google sheet to an extractor')
        self._add_debug_argument(copy_urls)
        self._add_extractor_id_argument(copy_urls)
        self._add_spread_sheet_id_argument(copy_urls)
        self._add_range_argument(copy_urls)
        copy_urls.set_defaults(which=CMD_COPY_URLS)

        #
        # EXTRACTOR
        #
        extract = subparser.add_parser(CMD_EXTRACT, help='Runs the full extraction process')
        self._add_debug_argument(extract)
        self._add_extractor_id_argument(extract)
        self._add_spread_sheet_id_argument(extract)
        self._add_range_argument(extract)
        extract.set_defaults(which=CMD_EXTRACT)

        #
        # EXTRACTOR START
        #
        extractor_start = subparser.add_parser(CMD_EXTRACTOR_START, help='Starts an extractor')
        self._add_debug_argument(extractor_start)
        self._add_extractor_id_argument(extractor_start)
        extractor_start.set_defaults(which=CMD_EXTRACTOR_START)

        #
        # Extractor Status
        #
        extractor_status = subparser.add_parser(CMD_EXTRACTOR_STATUS, help='Displays the status of recent craw runs')
        self._add_debug_argument(extractor_status)
        self._add_extractor_id_argument(extractor_status)
        extractor_status.set_defaults(which=CMD_EXTRACTOR_STATUS)

        #
        # EXTRACTOR URLS
        #
        extractor_urls = subparser.add_parser('extractor-urls', help='Displays the URLs from an extractor')
        self._add_debug_argument(extractor_urls)
        self._add_extractor_id_argument(extractor_urls)
        extractor_urls.set_defaults(which=CMD_EXTRACTOR_URLS)

        #
        # SHEET URLS
        #
        sheet_urls = subparser.add_parser(CMD_SHEET_URLS, help='Displays the URLs from a google sheet')
        self._add_debug_argument(sheet_urls)
        self._add_spread_sheet_id_argument(sheet_urls)
        self._add_range_argument(sheet_urls)
        sheet_urls.set_defaults(which=CMD_SHEET_URLS)

        args = parser.parse_args()

        if 'which' in args:
            self._command = args.which

        if 'extractor_id' in args:
            self._extractor_id = args.extractor_id

        if 'spread_sheet_id' in args:
            self._spread_sheet_id = args.spread_sheet_id

        if 'spread_sheet_range' in args:
            self._spread_sheet_range = args.spread_sheet_range

        if 'debug' in args:
            self._debug = args.debug

    def _copy_urls(self):
        """
        Copies URLs from a Google sheet to a Extractor URL list
        :return:
        """
        rc = 0
        self.copy_urls(self._spread_sheet_id, self._spread_sheet_range, self._extractor_id)
        return rc

    def _extract(self):
        """
        Extracts the URLs from the specified Google Sheet and range, adds to the
        specified Extractor and then run the Extractor
        :return:
        """
        rc = 0
        self.extract(self._spread_sheet_id, self._spread_sheet_range, self._extractor_id)
        rc = 0

    def _extractor_start(self):
        """
        Stars an extractor craw run from the provide extractor id
        :return:
        """
        rc = None
        result = self.extractor_start(self._extractor_id)
        if 'error' in result:
            print(result['error'])
            rc = 1
        else:
            print("craw run id: {0}".format(result))
            rc = 0
        return rc

    def _extractor_status(self):
        """
        Displays the crawl runs of an extractor
        :return:
        """
        rc = 0
        status = self.extractor_status(self._extractor_id)
        for s in status:
            print("guid: {0}, state: {1}, rows: {2}, total_urls: {3}, success_urls: {4}, failed_urls: {5}".format(
                    s['guid'], s['state'], s['rowCount'], s['totalUrlCount'], s['successUrlCount'],
                s['failedUrlCount']))
        return rc

    def _extractor_urls(self):
        """
        Display the URLs associated with the given extractor
        :return: None
        """
        rc = 0
        urls = self.extractor_urls(self._extractor_id)
        for url in urls:
            print(url)
        return rc

    def _sheet_urls(self):
        """
        Display the URLs associated with the given Google Sheet and range
        :return:
        """
        rc = 0
        urls = self.sheet_urls(self._spread_sheet_id, self._spread_sheet_range)
        for url in urls:
            print(url)
        return rc

    def _dispatch_sub_command(self):
        """
        Dispatch sub-command based on command line arguments
        :return:
        """
        return_code = None

        if self._debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.ERROR)
        logger.info("Running command: {0}".format(self._command))

        if self._command == CMD_COPY_URLS:
            return_code = self._copy_urls()
        elif self._command == CMD_EXTRACT:
            return_code = self._extract()
        elif self._command == CMD_EXTRACTOR_START:
            return_code = self._extractor_start()
        elif self._command == CMD_EXTRACTOR_STATUS:
            return_code = self._extractor_status()
        elif self._command == CMD_EXTRACTOR_URLS:
            return_code = self._extractor_urls()
        elif self._command == CMD_SHEET_URLS:
            return_code = self._sheet_urls()

        sys.exit(return_code)

    def execute(self):
        """
        Execute the functionality of the command line utility
        :return: None
        """
        self._handle_arguments()
        self._dispatch_sub_command()


def main():
    """
    Main entry point for command line tool
    :return:
    """
    g = GsExtractorUrls()
    g.execute()


if __name__ == '__main__':
    main()
