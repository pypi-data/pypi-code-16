import getopt

from bucketlist import speedyio
from bucketlist.utils import convert_int
from bucketlist.errors import BucketlistError
from bucketlist.providers import get_current_provider


class ViewCommand:
    __command_name__ = 'view'

    def __init__(self):
        pass

    def execute(self, argv):
        Provider = get_current_provider()

        optlist, args = getopt.getopt(argv, 'c:', ['count=', 'completed', 'help'])
        optmap = {
            opt[0].lstrip('-'): opt[1]
            for opt in optlist
        }

        if 'help' in optmap:
            print(
                "usage: bucket-list view [options]",
                "\n  options:",
                "\n    -c             category from which you want to view items",
                "\n    --count        maximum number ites to be fetched from your bucket list",
                "\n    --completed    fetches completed items from your bucket list",
                "\n    --help         prints help"
                )
            print(
                "\nFor more details you can refer official documentation here:",
                "\nhttps://github.com/arpitbbhayani/bucket-list/wiki/view"
                )
            return

        if 'c' not in optmap:
            options = [speedyio.Item(x.name, x) for x in Provider.get_categories()]
            if not options:
                raise BucketlistError("You have not added any item in your bucket list.")

            bucketlist_category = speedyio.chooseone(options, message="Select a category")
        else:
            bucketlist_category = Provider.get_category(optmap['c'])
            if bucketlist_category is None:
                speedyio.error("Category {} does not exist!".format(optmap['c']))
                return

        if 'completed' in optmap:
            bucketlist_items = Provider.get_items(bucketlist_category, completed=True)
        else:
            bucketlist_items = Provider.get_items(bucketlist_category, completed=False)

        count = optmap.get('count')
        if count is not None:
            count = convert_int(count)
            if count is None or count <= 0:
                speedyio.error("'count' should be a positive number.")
                return
            bucketlist_items = bucketlist_items[:count]

        for bucketlist_item in bucketlist_items:
            speedyio.bold_print(" - {}".format(bucketlist_item.message))
