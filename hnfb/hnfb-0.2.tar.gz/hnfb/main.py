import logging
import json
from concurrent import futures
from contextlib import ExitStack

import requests

from .utils import timed

logger = logging.getLogger(__name__)
BASE_URL = 'https://hacker-news.firebaseio.com/v0/'


# exceptions
class HNException(Exception):
    """Base HN Exception.
    """

class HNNotFoundException(HNException):
    """Not found exception.
    """
    pass


# main class
class HN(object):
    """Represents a HN Firebase Client.

    Simplifies fetching imformation from Hacker News API provided through Firebase.
    """

    @staticmethod
    def stories(base, page=1, page_size=50):
        """Fetches stories.

        Args:
            base (string): One of top, new, best, ask, show, or job.
            page (int): The page number used for pagination. Defaults to 1.
            page_size (int): The number of items to return per page. Defaults to 50.

        Returns:
            Stories: A Stories object.

        Raises:
            HnException: If invalid base is specified.

        """

        if base not in ('top', 'new', 'best', 'ask', 'show', 'job'):
            raise HNException('Invalid base specified.')

        url = BASE_URL + '{}stories.json'.format(base)

        request = requests.get(url)
        data = request.json()

        # paginate the data
        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        data = data[start_index:end_index]

        return Stories(base, page, page_size, data)

    @staticmethod
    def item(id):
        """Fetches an item.

        Args:
            id (int): The id of an item.

        Returns:
            Item: An Item object.

        Raises:
            HNNotFoundException: If item is not found.
        """

        url = BASE_URL + 'item/{}.json'.format(id)

        request = requests.get(url)
        data = request.json()

        if not data:
            raise HNNotFoundException('Item {} not found.'.format(id))

        return Item(id, data)

    @staticmethod
    def user(username):
        """Fetches a user.

        Args:
            username (string): The username of a user.

        Returns:
            User: A User object.

        Raises:
            HNNotFoundException: If user is not found.
        """
        url = BASE_URL + 'user/{}.json'.format(username)

        request = requests.get(url)
        data = request.json()

        if not data:
            raise HNNotFoundException('User {} not found.'.format(username))

        return User(username, data)

    @staticmethod
    def updates():
        """Fetches recent updates.

        Returns:
            Updates: An updates object.
        """
        url = BASE_URL + 'updates.json'

        request = requests.get(url)
        data = request.json()

        return Updates(data)


class Stories(object):
    """Represents HN stories.

    Not meant to be used directly.

    Attributes:
        base (str): Indicates a HN stories base.
        page (int): Page number.
        page_size (int): Page size.
        data (dict): Original response from Firebase.

    """

    def __init__(self, base, page, page_size, data):
        """Inits Stories with base, page, page_size, and data."""
        self.base = base
        self.page = page
        self.page_size = page_size
        self.data = data

    def expanded(self, max_workers=None):
        """Fetches data for each individual stories item.

        Returns:
            list: An expanded list of stories.
        """
        with ExitStack() as stack:
            exc = stack.enter_context(futures.ThreadPoolExecutor(max_workers=max_workers))
            session = requests.Session()

            urls = {id: BASE_URL + 'item/{}.json'.format(id) for id in self.data}
            futures_to_ids = {exc.submit(session.get, url): id for id, url in urls.items()}

            items = []
            for future in futures_to_ids:
                data = future.result().json()
                items.append(data)

        return items


class Item(object):
    """Represents HN item.

    Not meant to be used directly.

    Attributes:
        id (int): Item's id
        data (dict): Original response from Firebase.
    """

    def __init__(self, id, data):
        """Inits Item with id and data."""
        self.id = id
        self.data = data

    @staticmethod
    def _get_comments(kids, exc, session, depth):
        """Internal method to fetch comments recursively.
        """

        if not kids:
            raise HNNotFoundException('No comments found.')

        if depth is not None and depth < 1:
            raise HNNotFoundException('Comment depth reached')

        if depth is not None:
            depth -= 1

        urls = {id: BASE_URL + 'item/{}.json'.format(id) for id in kids}
        futures_to_ids = {exc.submit(session.get, url): id for id, url in urls.items()}

        items = []
        for future in futures_to_ids:
            data = future.result().json()

            try:
                comments = Item._get_comments(data.get('kids'), exc, session, depth)
                data['children'] = comments
            except HNException:
                pass

            items.append(data)

        return items

    def comments(self, page=1, page_size=50, depth=None, max_workers=None):
        """Fetches item's comments.

        Fetching is done concurrently using multiple workers.

        Arguments:
            page (int): The page number used for pagination. Defaults to 1.
            page_size (int): The number of items to return per page. Defaults to 50.
            depth (int): The number for the depth for comments.
                         For any given depth, a max of depth descendants will be returned.
            max_workers (int): Number of workers to use for fetching.
                               Defaults to None, meaning number of
                               processors on the machine x 5.

        Returns:
            list: A list of objects, each representing a comment. Each comment has a
                  `children` key representing it's children, if there are any and if depth isn't exceeded.
        """
        kids = self.data.get('kids')
        if not kids:
            raise HNNotFoundException('No comments found.')

        with ExitStack() as stack:
            exc = stack.enter_context(futures.ThreadPoolExecutor(max_workers=max_workers))
            session = stack.enter_context(requests.Session())

            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            kids = kids[start_index:end_index]

            try:
                items = Item._get_comments(kids, exc, session, depth)
            except HNNotFoundException:
                return []

        return items


class User(object):
    """Represents HN user.

    Not meant to be used directly.

    Attributes:
        _data (dict): Original response from Firebase.
    """

    def __init__(self, username, data):
        """Inits User with username and data."""
        self.username = username
        self.data = data


class Updates(object):
    """Represents HN recent updates.

    Not meant to be used directly.

    Attributes:
        items (list(int)): List of recently updated item ids.
        profiles (list(str)): List of recently updates user profile ids.
        _data (dict): Original response from Firebase.
    """
    def __init__(self, data):
        """Inits Updates with data."""
        self.data = data
