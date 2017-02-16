from bucketlist import appconfig
from bucketlist.decorators import dumptime
from bucketlist.errors import BucketlistError
from bucketlist.entities import BucketlistItem, BucketlistCategory
from bucketlist.providers.localfs import localfs_api


class LocalFS:
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

        folder_path = appconfig.get('provider_config', 'data-dir')
        localfs_api.validate_init(folder_path)

        if not localfs_api.category_exists(folder_path, category.name):
            localfs_api.create_category(folder_path, category.name)

        item_id = localfs_api.create_item(folder_path, category.name, item.message)

        return BucketlistItem(item_id, item.message, False)

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

        folder_path = appconfig.get('provider_config', 'data-dir')
        localfs_api.validate_init(folder_path)

        if not localfs_api.category_exists(folder_path, category.name):
            raise BucketlistError("Category {} does not exit.".format(category.name))

        items = localfs_api.get_items(folder_path, category.name, completed=completed)

        return [BucketlistItem(i['id'], i['message'], completed) for i in items]

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
        folder_path = appconfig.get('provider_config', 'data-dir')
        localfs_api.validate_init(folder_path)

        return [BucketlistCategory(name) for name in localfs_api.get_categories(folder_path)]

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

        categories = LocalFS.get_categories()
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

        folder_path = appconfig.get('provider_config', 'data-dir')
        localfs_api.validate_init(folder_path)

        if localfs_api.category_exists(folder_path, category_name):
            raise BucketlistError("Category {} already exists.".format(category_name))

        localfs_api.create_category(folder_path, category_name)

        return BucketlistCategory(category_name)

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

        folder_path = appconfig.get('provider_config', 'data-dir')
        localfs_api.validate_init(folder_path)

        if not localfs_api.category_exists(folder_path, category.name):
            raise BucketlistError("Category {} does not exists.".format(category.name))

        task = localfs_api.update_item(folder_path, category.name, item.id, completed=True)
        return BucketlistItem(task['id'], task['message'], task['completed'])

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

        folder_path = appconfig.get('provider_config', 'data-dir')
        localfs_api.validate_init(folder_path)

        if not localfs_api.category_exists(folder_path, category.name):
            raise BucketlistError("Category {} does not exists.".format(category.name))

        task = localfs_api.get_item(folder_path, category.name, item_id)
        if task is None:
            return None
        return BucketlistItem(task['id'], task['message'], task['completed'])

    @staticmethod
    @dumptime
    def clean():
        """
        Removes all items and any metadata created in your provider.
        Returns:
            None
        """
        folder_path = appconfig.get('provider_config', 'data-dir')
        localfs_api.validate_init(folder_path)
        localfs_api.delete_folder(folder_path)

    @staticmethod
    @dumptime
    def init():
        """
        Initializes the provider. It sets up all necessary items/metadata in
        the provider.
        Returns:
            None
        """
        folder_path = appconfig.get('provider_config', 'data-dir')

        try:
            localfs_api.validate_init(folder_path)
        except BucketlistError as e:
            if e.error_code == 'file_instead_of_folder':
                raise e

        if not localfs_api.folder_exists(folder_path):
            localfs_api.create_folder(folder_path)
