#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2016 juxor <ju@riseup.net>

# This file is part of afaq-dl.
#
# afaq-dl is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# afaq-dl is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with afaq-dl.  If not, see <http://www.gnu.org/licenses/>.

""""""
import logging
from bs4 import BeautifulSoup as BS
from lxml import etree as ET
#from scrapy.utils.project import get_project_settings


#settings = get_project_settings()
logger = logging.getLogger(__name__)
#logger.debug('setting from html %s', settings.get('HTML_WRAPPER'))

__all__ = ['clean_html_ucontent',
     'create_html_page',
     'create_html_page_bs',
     'create_html_page_et']

HTML_WRAPPER = """<!DOCTYPE html>
<html>
  <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  </head>
  <body>
  </body>
</html>"""

HTML_HEAD = """  <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  </head>"""

HTML_WRAPPER_VAR = u"""<!DOCTYPE html>
<html>
  <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  {0}
  </head>
  <body>
  {1}
  </body>
</html>"""

ADOBE_TEXT = \
"""<p>
To view and print out the file you will need to have<br>
Adobe Document Reader on your computer. This is free<br>
software that now comes on many computers and with<br>
many CD's. If you do not already have it you can<br>
<a href="http://www.adobe.com/products/acrobat/readstep.html"><br>
download it from the Adobe site.</a><br>
[or<br>
<a href="http://www.adobe.com/products/acrobat/alternate.html"><br>
click here for a faster text only page</a>]
</p>"""


def create_html_page_bs(ucontent, utitle):
    head = BS(HTML_HEAD, 'lxml')
    head.append(utitle)
    ucontent = clean_html_ucontent(ucontent)
    # BS creates htmlm and body tags
    page = BS(ucontent, 'lxml')
    page.setup(page.body, head)
    html_page = page.prettify()
    return html_page


def clean_html_ucontent(ucontent):
    # remove trailing whitespaces
    ucontent = "\n".join([line.rstrip() for line in
                             ucontent.split('\n')])
    # fix wrong tag
    ucontent = ucontent.replace('<title></title>', '')
    # fix links
    ucontent = ucontent.replace('<a href="/afaq/', '<a href="')
    ucontent = ucontent.replace(
                    'http://anarchism.pageabode.com/afaq/', '')
    # fix blog link
    ucontent = ucontent.replace(
                    '../../../../../../blogs/afaq',
                    'http://www.anarchism.pageabode.com/blogs/afaq')
    # remove privative software ad
    ucontent = ucontent.replace(ADOBE_TEXT, '')
    return ucontent


def create_html_page_et(ucontent, utitle):
    html_page = ET.fromstring(HTML_WRAPPER)
    head, body = list(html_page)
    head.append(ET.fromstring(utitle))
    ucontent = clean_html_ucontent(ucontent)
    content_et = ET.fromstring(ucontent)
    body.append(content_et)
    html = ET.tostring(html_page, encoding='unicode', pretty_print=True)
    # TODO: find why this happen
#    html = html.replace('<p/>','<p></p>')
    return html


def create_html_page(ucontent, utitle):
    ucontent = clean_html_ucontent(ucontent)
    html_page = HTML_WRAPPER_VAR.format(utitle, ucontent)
    return html_page
