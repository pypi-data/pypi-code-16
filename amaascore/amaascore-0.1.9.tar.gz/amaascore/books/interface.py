from __future__ import absolute_import, division, print_function, unicode_literals

import logging

from amaascore.books.utils import json_to_book
from amaascore.config import ENDPOINTS
from amaascore.core.interface import Interface


class BooksInterface(Interface):

    def __init__(self, logger=None):
        endpoint = ENDPOINTS.get('books')
        self.logger = logger or logging.getLogger(__name__)
        super(BooksInterface, self).__init__(endpoint=endpoint)

    def new(self, book):
        url = self.endpoint + '/books'
        response = self.session.post(url, json=book.to_interface())
        if response.ok:
            book = json_to_book(response.json())
            return book
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def amend(self, book):
        url = '%s/books/%s/%s' % (self.endpoint, book.asset_manager_id, book.book_id)
        response = self.session.put(url, json=book.to_interface())
        if response.ok:
            book = json_to_book(response.json())
            return book
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def retrieve(self, asset_manager_id, book_id):
        url = '%s/books/%s/%s' % (self.endpoint, asset_manager_id, book_id)
        response = self.session.get(url)
        if response.ok:
            return json_to_book(response.json())
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def retire(self, asset_manager_id, book_id):
        url = '%s/books/%s/%s' % (self.endpoint, asset_manager_id, book_id)
        json = {'book_status': 'Retired'}
        response = self.session.patch(url, json=json)
        if response.ok:
            return json_to_book(response.json())
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def search(self, asset_manager_ids=None, book_ids=None):
        search_params = {}
        # Potentially roll this into a loop through args rather than explicitly named - depends on additional validation
        if asset_manager_ids:
            search_params['asset_manager_ids'] = asset_manager_ids
        if book_ids:
            search_params['book_ids'] = book_ids
        url = self.endpoint + '/books'
        response = self.session.get(url, params=search_params)
        if response.ok:
            books = [json_to_book(json_book) for json_book in response.json()]
            return books
        else:
            self.logger.error(response.text)
            response.raise_for_status()

    def books_by_asset_manager(self, asset_manager_id):
        url = '%s/books/%s' % (self.endpoint, asset_manager_id)
        response = self.session.get(url)
        if response.ok:
            books = [json_to_book(json_book) for json_book in response.json()]
            return books
        else:
            self.logger.error(response.text)
            response.raise_for_status()
