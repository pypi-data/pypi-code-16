# Created By - Karan Dev
# Date - Feb 22, 2017
import logging

logging.captureWarnings(True)

import sys
import webbrowser
import requests
import re
import os

YOUTUBE_URL = 'https://youtube.com'
# https://www.youtube.com/results?search_query=cheap+thrills

class GaanaCli:

    def __init__(self):
        self._song_listing_url = ''

    def play_process(self):

        if len(sys.argv) != 2:
            print "Wrong argument - Write gaanacli \"song name\""
            return 0

        self._song_listing_url = YOUTUBE_URL + '/results?search_query=' + sys.argv[1]
        lto = self.get_link_to_open()

    def get_link_to_open(self):
        resp = requests.get(self._song_listing_url)

        result = re.findall('href=\"/watch\?v=[a-zA-Z0-9-_]+', resp.text)
        if not result:
            print "No song found"
            return 0
        link_list = result[0].replace('href="', '')

        savout = os.dup(1)
        os.close(1)
        os.open(os.devnull, os.O_RDWR)
        try:
            webbrowser.open( YOUTUBE_URL + link_list, new=0, autoraise=False )
            print "Song played."
        finally:
            os.dup2(savout, 1)


def main():
    obj = GaanaCli()
    obj.play_process()
    sys.exit(0)

if __name__ == "__main__":
    main()