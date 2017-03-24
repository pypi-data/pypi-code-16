# -*- coding: utf-8 -*-#
# March 19 2016,  <chopps@gmail.com>
#
# Copyright (c) 2016 by Christian E. Hopps.
# All rights reserved.
#
# REDISTRIBUTION IN ANY FORM PROHIBITED WITHOUT PRIOR WRITTEN
# CONSENT OF THE AUTHOR.
#
from __future__ import absolute_import, division, unicode_literals, print_function, nested_scopes
import json
try:
    import urllib2 as urllib
except:
    import urllib as urllib

# $curl_wg =
# "curl 'https://datatracker.ietf.org/api/v1/doc/state/?format=json&limit=0&type__slug__in=draft-stream-ietf' 2> /dev/null";
# $curl_iesg =
# "curl 'https://datatracker.ietf.org/api/v1/doc/state/?format=json&limit=0&type__slug__in=draft-iesg' 2> /dev/null";
# $curl_rfc_editor =
# "curl 'https://datatracker.ietf.org/api/v1/doc/state/?format=json&limit=0&type__slug__in=draft-rfceditor' 2> /dev/null";

# get_states( $curl_rfc_editor, 'RFC' );
# get_states( $curl_iesg,       'IESG' );
# get_states( $curl_wg,         'WG' );

url = "https://datatracker.ietf.org/api/v1/doc/document/?format=json&name__contains=draft-ietf-{}&expires__gt={}&limit=0"
url = url.format("isis", "2016-03-19")
result = json.load(urllib.urlopen(url))
import pdb
pdb.set_trace()
# [ x['name'] for x in result['objects'] ]


__author__ = ''
__date__ = 'March 19 2016'
__version__ = '1.0'
__docformat__ = "restructuredtext en"
