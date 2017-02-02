# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import requests

def get_changeset(channel, build_id):
    # http://ftp.mozilla.org/pub/firefox/nightly/2016/10/2016-10-01-03-04-30-mozilla-central/firefox-52.0a1.en-US.win32.txt
    # http://ftp.mozilla.org/pub/firefox/nightly/2016/10/2016-10-01-00-40-00-mozilla-aurora/firefox-51.0a2.en-US.win32.txt
    # http://ftp.mozilla.org/pub/firefox/candidates/50.0b3-candidates/build1/win32/en-US/firefox-50.0b3.txt (there might be other builds)
    # http://ftp.mozilla.org/pub/firefox/candidates/49.0-candidates/build1/win32/en-US/firefox-49.0.txt (RC1)
    # http://ftp.mozilla.org/pub/firefox/candidates/49.0-candidates/build2/win32/en-US/firefox-49.0.txt (RC2)
    # http://ftp.mozilla.org/pub/firefox/candidates/49.0-candidates/build3/win32/en-US/firefox-49.0.txt (RC3)
    # http://ftp.mozilla.org/pub/firefox/candidates/49.0-candidates/build4/win32/en-US/firefox-49.0.txt (release)

    requests.get()

def get_buildid(channel, changeset):
    pass
