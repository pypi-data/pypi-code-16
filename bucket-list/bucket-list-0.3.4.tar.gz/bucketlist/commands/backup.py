import json
import getopt

from bucketlist import speedyio, appconfig
from bucketlist.errors import BucketlistError
from bucketlist.providers import get_current_provider


class BackupCommand:
    __command_name__ = 'backup'

    def dump(self, data, file_path):
        with open(file_path, 'w') as f:
            json.dump(data, f, sort_keys=True, indent=4)

    def execute(self, argv):
        Provider = get_current_provider()

        optlist, args = getopt.getopt(argv, '', ['file=', 'help'])
        optmap = {
            opt[0].lstrip('-'):opt[1]
            for opt in optlist
        }

        if 'help' in optmap:
            print(
                "usage: bucket-list backup [options]",
                "\n  options:",
                "\n    --file   absolute path of backup file",
                "\n    --help   prints help"
                )
            print(
                "\nFor more details you can refer official documentation here:",
                "\nhttps://github.com/arpitbbhayani/bucket-list/wiki/backup"
                )
            return

        if 'file' not in optmap:
            optmap['file'] = speedyio.askfor('file', empty_allowed=False)

        try:
            with open(optmap['file'], 'w') as f:
                f.write('')
        except Exception as e:
            raise BucketlistError(str(e))

        provider_name = appconfig.get('provider', 'name')
        backup_data = {
            'provider': provider_name,
        }

        data = {}
        categories = Provider.get_categories()
        speedyio.info("{} categories fetched".format(len(categories)))
        for category in categories:

            tasks_incomplete = Provider.get_items(category, completed=False)
            speedyio.info("{} incomplete items fetched for category {}".format(len(tasks_incomplete), category.name))

            tasks_complete = Provider.get_items(category, completed=True)
            speedyio.info("{} completed items fetched for category {}".format(len(tasks_complete), category.name))

            data[category.name] = [t.__dict__ for t in tasks_incomplete + tasks_complete]

        backup_data['data'] = data

        self.dump(backup_data, optmap['file'])
        speedyio.success("Backup successfully created at {}".format(optmap['file']))
