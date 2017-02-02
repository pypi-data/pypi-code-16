from bucketlist import appconfig
from bucketlist.decorators import dumptime
from bucketlist.errors import BucketlistError
from bucketlist.entities import BucketlistItem, BucketlistCategory
from bucketlist.providers.wunderlist import wunderlist_api
from bucketlist.providers.wunderlist import WRequests as wrequests


class Wunderlist:
    @staticmethod
    @dumptime
    def add_item(category, item):
        """
        Adds item `item` to category `category` in your Bucket List.
        Args:
            category: Category to which message should belong.
                      type -> BucketlistCategory
            item: Item to be stored in Bucket List under category `category`.
                   type -> BucketlistItem
        Returns:
            Returns item saved in your Bucket List.
            type -> BucketlistItem
        """
        assert type(category) == BucketlistCategory
        assert type(item) == BucketlistItem

        folder_name = appconfig.get('provider_config', 'folder-name')
        folder = wunderlist_api.get_folder(folder_name)

        try:
            wlist = wunderlist_api.get_list(folder, category.name)
        except BucketlistError:
            wlist = wunderlist_api.create_list(folder, category.name)

        task = wunderlist_api.create_task(wlist, item.message)
        return BucketlistItem(str(task['id']), task['title'], task['completed'])

    @staticmethod
    @dumptime
    def get_items(category, completed=False):
        """
        Gets all items from your Bucket List that belongs to
        category `category`.
        Args:
            category: Category.
                      type -> BucketlistCategory
        Keyword Args:
            completed: if True -> fetches all completed items from Bucket List
                       other wise fetches Pending items
        Returns:
            Returns list of items that saved in your Bucket List.
            type -> List<BucketlistItem>
        """
        assert type(category) == BucketlistCategory

        folder_name = appconfig.get('provider_config', 'folder-name')
        folder = wunderlist_api.get_folder(folder_name)

        wlist = wunderlist_api.get_list(folder, category.name)
        tasks = wunderlist_api.get_tasks(wlist, completed=completed)

        return [BucketlistItem(str(task['id']), task['title'], task['completed']) for task in tasks]

    @staticmethod
    @dumptime
    def get_categories():
        """
        Gets all items from your Bucket List that belongs to
        category `category`.
        Returns:
            Returns list of categories in your Bucket List.
            type -> List<BucketlistCategory>
        """
        folder_name = appconfig.get('provider_config', 'folder-name')
        folder = wunderlist_api.get_folder(folder_name)

        return [BucketlistCategory(l.get('title')) for l in wunderlist_api.get_lists(folder)]

    @staticmethod
    @dumptime
    def get_category(category_name):
        """
        Returns category where name is `category_name` from your Bucket List.
        If category is not present, the function returns None
        Args:
            category_name: Category.
                           type -> str
        Returns:
            Returns category with name `category_name` stored in
            your Bucket List.
            type -> List<BucketlistItem>
        """
        type(category_name) == str

        categories = Wunderlist.get_categories()
        for category in categories:
            if category.name == category_name:
                return category
        return None

    @staticmethod
    @dumptime
    def create_category(category_name):
        """
        Creates a category with name `category_name` in your Bucket List if
        any category with same name do not already exist.
        Args:
            category_name: Category name.
                           type -> str
        Returns:
            Returns category saved in your Bucket List.
            type -> BucketlistCategory
        """
        type(category_name) == str

        folder_name = appconfig.get('provider_config', 'folder-name')
        folder = wunderlist_api.get_folder(folder_name)

        try:
            wlist = wunderlist_api.get_list(folder, category_name)
        except BucketlistError:
            wlist = wunderlist_api.create_list(folder, category_name)

        return BucketlistCategory(wlist.get('title'))

    @staticmethod
    @dumptime
    def mark_as_complete(category, item):
        """
        Marks an item `item` belonging to category `category` as complete
        in your Bucket List.
        Args:
            category: Category to which message should belong.
                      type -> BucketlistCategory
            item: Item to be marked as complete.
                   type -> BucketlistItem
        Returns:
            Returns updated item `item` in your Bucket List.
            type -> BucketlistItem
        """
        assert type(category) == BucketlistCategory
        assert type(item) == BucketlistItem

        task = wunderlist_api.update_task(item.id, completed=True)
        return BucketlistItem(str(task['id']), task['title'], task['completed'])

    @staticmethod
    @dumptime
    def get_item(category, item_id):
        """
        Returns item with id `item_id` belonging to category `category`
        from your Bucket List. If item is not present, the function
        returns None
        Args:
            category: Category to which item belongs.
                      type -> BucketlistCategory
            item_id: Id of the item that is to be fetched.
                     type -> str
        Returns:
            Returns item with id `item_id` stored in your Bucket List.
            type -> BucketlistItem
        """
        assert type(category) == BucketlistCategory
        assert type(item_id) == str

        task = wunderlist_api.get_task(item_id)
        if task is None:
            return None
        return BucketlistItem(str(task['id']), task['title'], task['completed'])

    @staticmethod
    @dumptime
    def clean():
        """
        Removes all items and any metadata created in your provider.
        Returns:
            None
        """
        folder_name = appconfig.get('provider_config', 'folder-name')
        folder = wunderlist_api.get_folder(folder_name)

        wlists = wunderlist_api.get_lists(folder)
        for l in wlists:
            wunderlist_api.delete_list(l['id'])

    @staticmethod
    @dumptime
    def init():
        """
        Initializes the provider. It sets up all necessary items/metadata in
        the provider.
        Returns:
            None
        """
        folder_name = appconfig.get('provider_config', 'folder-name')
        try:
            folder = wunderlist_api.get_folder(folder_name)
        except BucketlistError:
            wlist = wunderlist_api.create_dummy_list()
            folder = wunderlist_api.create_folder(folder_name, [wlist.get('id')])
