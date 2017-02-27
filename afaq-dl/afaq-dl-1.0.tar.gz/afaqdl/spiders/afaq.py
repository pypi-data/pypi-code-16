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
import io
import logging
from os import makedirs
from os.path import join, isdir

import scrapy
from scrapy.http import Request
# from scrapy.utils.project import get_project_settings

from afaqdl.utils import html_util
from afaqdl import conf


# settings = get_project_settings()
logger = logging.getLogger(__name__)


class AfaqSpider(scrapy.Spider):
    name = "afaq"
    allowed_domains = [conf.DOMAIN]
    start_urls = [conf.URL]

    # NOTE: add arguments here to be accepted as command line arguments
    def __init__(self, *args, **kwargs):
        super(AfaqSpider, self).__init__(*args, **kwargs)
        # logger.debug('settings %s', settings.items())
        logger.debug('HTML_PATH %s', conf.HTML_PATH)
        if not isdir(conf.HTML_PATH):
            makedirs(conf.HTML_PATH)

    def parse(self, response):
        utitle = response.selector.xpath('//title').extract_first()
        ucontent = response.xpath(
                       conf.XPATH_CONTENT).extract_first()
        page = response.url.split("/")[-1]
        filepath = join(conf.HTML_PATH, page)
        html = html_util.create_html_page(ucontent, utitle)
        with io.open(filepath, 'w') as f:
            f.write(html)
        logger.info('Saved file %s.', filepath)

        next_page = response.xpath(conf.XPATH_NEXT).extract_first()
        logger.debug('Next page %s.', next_page)
        if next_page:
            yield Request(
                response.urljoin(next_page),
                callback=self.parse,
            )
        else:
            logger.debug('No next page.')
