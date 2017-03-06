# -*- coding: utf-8 -*-
"""
    tengri.weather
    -----------------

    Display weather forecast for specified location.

    :copyright: (c) 2017 by Robert Durkaj.
    :license: MIT, see the LICENSE for more details.
"""
from __future__ import print_function
import argparse
import random

import requests
from lxml import html

from tengri import web
from tengri import __version__

NOT_FOUND = '<not found>'
GOOGLE_SEARCH_URL = 'http://www.google.com/search?q={0}'
NO_RESULTS = '<no results>'
NO_RESULTS_MSG = 'Place not found on site'


def _load_value(xpath, root):
    """ Return text content of the first element specified by `xpath`.
    :param str xpath: XPath of the element.
    :param root: Root element.
    """

    element = root.find(xpath)  # type: html.HtmlElement
    if element is None:
        return NOT_FOUND
    value = element.text_content()
    value = ' '.join(value.split())  # remove unwanted space characters
    return value


def _load_root_from_file(path):
    """ Return root element from HTML file.
    :param str path: The path of HTML file.
    """

    tree = html.parse(path)
    root = tree.getroot()  # type: html.HtmlElement
    return root


def _load_root_from_string(text):
    """ Return root element of HTML passed as `text`. """

    root = html.fromstring(text)
    return root


def load_html(page, htmltext):
    """ Return values found in HTML response. """

    root = _load_root_from_string(htmltext)
    values = []
    for label, xpath in page['lines']:
        value = _load_value(xpath, root)
        if value is not NOT_FOUND:
            values.append((label, value))
    return values


def get_response(url):
    """ Return HTML response from `url`. """

    user_agent = random.choice(web.USER_AGENTS)
    headers = {'User-Agent': user_agent}
    r = requests.get(url, headers=headers, timeout=2.0)

    # TODO use logging
    # print '\nRequesting: {0}'.format(url)
    # print 'User-Agent: {0}'.format(user_agent)
    # print 'content-type: {0}'.format(r.headers['content-type'])
    # print 'headers: {0}'.format(r.headers)
    # print 'history: {0}'.format(r.history)
    # print 'Response: {0}\n'.format(r.status_code)

    return r


def prepare_query(site, place):
    """ Return search query for `site` and `place`. """

    query = 'site:{0}+{1}'.format(site, place)
    return GOOGLE_SEARCH_URL.format(query)


def get_first_link(root):
    """ Return first result from `root` element. """

    a = root.find('.//*[@class="r"]/a')
    if a is None:
        return NO_RESULTS
    return a.attrib['href']


def forecast_page(page, place):
    """ Process weather forecast for `page` and `place. Print all values. """

    site = page['site']
    print('\n{0}'.format(site))
    print('-' * len(site))

    try:
        url = prepare_query(site, place)
        r = get_response(url)
        root = _load_root_from_string(r.text)
        link_url = get_first_link(root)
        if link_url == NO_RESULTS:
            print(NO_RESULTS_MSG)
            return

        r = get_response(link_url)

        values = load_html(page, r.text)
        for label, value in values:
            print(u'{0}: {1}'.format(label, value))
    except requests.exceptions.ConnectionError:
        print('Network connection error')


def forecast(place, show_version=True):
    """ Main forecast function. """

    print('\nTengri weather report for: "{0}"'.format(place))

    if show_version:
        print('version {0}'.format(__version__))

    for page in web.weather_pages():
        forecast_page(page, place)
    print('')


def get_valid_place(place):
    """ Return valid place.

    Strip spaces and check for empty value."""

    place = place.strip()
    if not place:
        raise ValueError('empty string')

    return place


def get_arg_parser():
    """ Return cmd argument parser. """

    text = 'Display weather forcasts for specified location'
    parser = argparse.ArgumentParser(description=text)
    info = 'Location for weather forecast'
    parser.add_argument('place', nargs='+', help=info)
    return parser


def cmd_launcher():
    """ Main entry point of application. """

    parser = get_arg_parser()
    args = parser.parse_args()
    place = ' '.join(args.place)

    place = get_valid_place(place)
    forecast(place)
