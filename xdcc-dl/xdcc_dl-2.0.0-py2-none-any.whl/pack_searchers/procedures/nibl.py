u"""
LICENSE:
Copyright 2016 Hermann Krumrey

This file is part of xdcc_dl.

    xdcc_dl is a program that allows downloading files via the XDCC
    protocol via file serving bots on IRC networks.

    xdcc_dl is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    xdcc_dl is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with xdcc_dl.  If not, see <http://www.gnu.org/licenses/>.
LICENSE
"""

# imports
from __future__ import absolute_import
import requests
from typing import List
from bs4 import BeautifulSoup
from xdcc_dl.entities.XDCCPack import XDCCPack
from xdcc_dl.entities.IrcServer import IrcServer
from requests.packages.urllib3 import disable_warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning


def find_nibl_packs(search_phrase):
    u"""
    Searches for XDCC Packs matching the specified search string on nibl.co.uk

    :param search_phrase: The search phrase to search for
    :return:              The list of found XDCC Packs
    """

    # Prepare the search term, nibl.co.uk uses + symbols as spaces.
    split_search_term = search_phrase.split(u" ")
    prepared_search_term = split_search_term[0]
    i = 1
    while i < len(split_search_term):
        prepared_search_term += u"+" + split_search_term[i]
        i += 1

    # Get the data from the website

    url = u"http://nibl.co.uk/bots.php?search=" + prepared_search_term

    # Since nibl.com has some sort of issue with their SSL certificate, we get the
    # HTML content without verifying the SSL cert. Additionally, the warning that
    # gets printed by default if you do that is suppressed
    disable_warnings(InsecureRequestWarning)
    html = requests.get(url, verify=False).text

    content = BeautifulSoup(html, u"html.parser")
    file_names = content.select(u".filename")
    pack_numbers = content.select(u".packnumber")
    bot_names = content.select(u".botname")
    file_sizes = content.select(u".filesize")

    results = []
    i = 0  # We need a counter variable since we have four lists of data

    while i < len(file_names):

        # The filename has two links after it, which need to be cut out
        filename = file_names[i].text.rsplit(u" \n", 1)[0]

        # The bot name has a link after it, which needs to be cut out
        bot = bot_names[i].text.rsplit(u" ", 1)[0]

        server = u"irc.rizon.net"
        packnumber = int(pack_numbers[i].text)
        size = file_sizes[i].text

        result = XDCCPack(IrcServer(server), bot, packnumber)
        result.set_size(size)
        result.set_filename(filename)
        results.append(result)
        i += 1

    return results
