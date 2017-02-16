import re
import getopt
from bucketlist import speedyio
from bucketlist.errors import BucketlistError
from bucketlist.entities import BucketlistItem, BucketlistCategory
from bucketlist.providers import get_current_provider


def validate_cateogry_name(category_name):
    CATEGORY_NAME_REGEX = '^[a-zA-Z0-9-]+$'
    if len(category_name) > 32 or re.match(CATEGORY_NAME_REGEX, category_name) is None:
        raise BucketlistError("'{}' does not comply with regular expression {} or its length is greater thatn 32"
                              .format(category_name, CATEGORY_NAME_REGEX))


class AddCommand:
    __command_name__ = 'add'

    def execute(self, argv):
        Provider = get_current_provider()

        optlist, args = getopt.getopt(argv, 'm:c:', ['help'])
        optmap = {
            opt[0].lstrip('-'): opt[1]
            for opt in optlist
        }

        if 'help' in optmap:
            print(
                "usage: bucket-list add [options]",
                "\n  options:",
                "\n    -m       message to be stored in your bucket list",
                "\n    -c       category to which the item should belong",
                "\n    --help   prints help"
                )
            print(
                "\nFor more details you can refer official documentation here:",
                "\nhttps://github.com/arpitbbhayani/bucket-list/wiki/add"
                )
            return

        if 'c' not in optmap:
            options = [speedyio.Item(x.name, x) for x in Provider.get_categories()]
            if not options:
                raise BucketlistError("No categories found!" +
                                      "\nIf you want to add item to a new category use option -c" +
                                      "\n    Example: bucket-list add -c animated-movies -m Bolt")

            bucketlist_category = speedyio.chooseone(options, message="Select a category")
        else:
            # Validating category name
            validate_cateogry_name(optmap['c'])

            bucketlist_category = Provider.get_category(optmap['c'])
            if bucketlist_category is None:
                bucketlist_category = Provider.create_category(optmap['c'])

        if 'm' not in optmap:
            optmap['m'] = speedyio.askfor('message', empty_allowed=False)

        bucketlist_item = Provider.add_item(
                              bucketlist_category,
                              BucketlistItem(None, optmap['m'], False)
                          )
        speedyio.success("'{}' added successfully \u2713".format(bucketlist_item.message))
