import json
import getopt

from bucketlist import speedyio, appconfig, logger
from bucketlist.providers import get_current_provider
from bucketlist.entities import BucketlistItem
from bucketlist.errors import BucketlistError


def validate_backedup_data(backedup_data):
    if 'data' not in backedup_data:
        raise BucketlistError("Invalid backup file.")

    if type(backedup_data['data']) != dict:
        raise BucketlistError("Invalid backup file.")


class RestoreCommand:
    __command_name__ = 'restore'

    def __init__(self):
        pass

    def read(self, file_path):
        try:
            with open(file_path, 'r') as f:
                return json.loads(f.read())
        except Exception as e:
            raise BucketlistError("{} is not a valid backup file".format(file_path))

    def execute(self, argv):
        Provider = get_current_provider()

        optlist, args = getopt.getopt(argv, '', ['file=', 'help'])
        optmap = {
            opt[0].lstrip('-'):opt[1]
            for opt in optlist
        }

        if 'help' in optmap:
            print(
                "usage: bucket-list restore [options]",
                "\n  options:",
                "\n    --file   absolute path of your backup file to be restored",
                "\n    --help   prints help"
                )
            print(
                "\nFor more details you can refer official documentation here:",
                "\nhttps://github.com/arpitbbhayani/bucket-list/wiki/restore"
                )
            return

        if 'file' not in optmap:
            optmap['file'] = speedyio.askfor('file', empty_allowed=False)

        provider_name = appconfig.get('provider', 'name')
        backedup_data = self.read(optmap['file'])

        try:
            Provider.clean()
            speedyio.info("Cleanup done")

            Provider.init()
            speedyio.info("Provider initialized")

            validate_backedup_data(backedup_data)

            for category_name, items in backedup_data.get('data').items():
                speedyio.info("Restoring data for category {}".format(category_name))
                category = Provider.get_category(category_name)
                if category is None:
                    category = Provider.create_category(category_name)

                for item in items:
                    bucketlist_item = Provider.get_item(category, item['id'])
                    if bucketlist_item is None:
                        bucketlist_item = Provider.add_item(category, BucketlistItem(None, item['message'], False))

                    if bucketlist_item.is_completed == False and item['is_completed'] == True:
                        Provider.mark_as_complete(category, bucketlist_item)

        except BucketlistError as e:
            speedyio.error("Data restored failed from {}.\nPlease try again.".format(optmap['file']))
            speedyio.error(e.description)
        except Exception as e:
            logger.exception(e)
            speedyio.error("Data restored failed from {}.\nPlease check logs ({}).".format(optmap['file'], appconfig.get('logging', 'file')))
        else:
            speedyio.success("Data restored from {}".format(optmap['file']))
