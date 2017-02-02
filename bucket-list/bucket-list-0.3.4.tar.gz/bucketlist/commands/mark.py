import getopt

from bucketlist import speedyio
from bucketlist.providers import get_current_provider


class MarkCommand:
    __command_name__ = 'mark'

    def __init__(self):
        pass

    def execute(self, argv):
        Provider = get_current_provider()

        optlist, args = getopt.getopt(argv, 'c:', ['help'])
        optmap = {
            opt[0].lstrip('-'):opt[1]
            for opt in optlist
        }

        if 'help' in optmap:
            print(
                "usage: bucket-list mark [options]",
                "\n  options:",
                "\n    -c       category to which the item belongs",
                "\n    --help   prints help"
                )
            print(
                "\nFor more details you can refer official documentation here:",
                "\nhttps://github.com/arpitbbhayani/bucket-list/wiki/mark"
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

        bucketlist_items = Provider.get_items(bucketlist_category, completed=False)
        options = [speedyio.Item(bucketlist_item.message, bucketlist_item) for bucketlist_item in bucketlist_items]
        if not options:
            return

        bucketlist_item = speedyio.chooseone(options, message="Mark as complete")

        bucketlist_item = Provider.mark_as_complete(bucketlist_category, bucketlist_item)
        speedyio.success("Marked as completed \u2713")
