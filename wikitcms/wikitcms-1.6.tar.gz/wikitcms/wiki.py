# Copyright (C) 2014 Red Hat
#
# This file is part of wikitcms.
#
# wikitcms is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Adam Williamson <awilliam@redhat.com>

from . import page

import mwclient
import re

class Wiki(mwclient.Site):
    """Extends the mwclient.Site class with some extra capabilities."""

    def write_page(self, page, content="Page created by wikitcms.", summary='',
                   force=False, section=None):
        """Write a full page, with the given content and summary. Takes 'force'
        parameter which will overwrite an existing page if true; otherwise the
        method will bail with an error. Raises underlying exception on failure.
        On attempt to write to an existing page without force=True, error will
        be mwclient.errors.APIError, with args[0] 'articleexists'. Does not
        return anything.
        """
        kwargs = dict()
        if force is False:
            kwargs['createonly'] = 'True'
        if section:
            kwargs['section'] = section

        try:
            page.save(content, summary=summary, **kwargs)
        except mwclient.EditError as e:
            # Handle captchas. The captcha plugin used on the Fedora wiki
            # helpfully gives us the question we have to answer...
            question = e.args[1]['captcha']['question']
            # ...but just for fun, with a unicode "minus" symbol.
            question = question.replace(u'\u2212', u'-')
            captchaid = e.args[1]['captcha']['id']
            if question:
                answer = eval(question)
                page.save(content, summary=summary, captchaword=answer,
                          captchaid=captchaid, **kwargs)
            else:
                raise

    def add_to_category(self, page_name, category_name, summary=''):
        """Add a given page to a given category if it is not already a member.
        Takes strings for the names of the page and the category, not mwclient
        objects.
        """
        page = self.pages[page_name]
        text = page.edit().encode('utf-8')
        if category_name not in text:
            text += "\n[[" + category_name + "]]"
            self.write_page(page, text, summary, True)

    def walk_category(self, category):
        """Simple recursive category walk. Returns a set of page objects that
        are members of the parent category or its sub-categories, to any level
        of recursion. 14 is the Category: namespace.
        """
        pages = set()
        for page in category:
            if page.namespace == 14:
                sub_pages = self.walk_category(page)
                for sub_page in sub_pages:
                    pages.add(sub_page)
            else:
                pages.add(page)
        return pages
