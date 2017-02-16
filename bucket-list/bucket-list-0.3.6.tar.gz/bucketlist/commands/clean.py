import getopt
from bucketlist import appconfig, speedyio
from bucketlist.providers import get_current_provider


class CleanCommand:
    __command_name__ = 'clean'

    def execute(self, argv):
        Provider = get_current_provider()

        optlist, args = getopt.getopt(argv, '', ['help'])
        optmap = {
            opt[0].lstrip('-'): opt[1]
            for opt in optlist
        }

        if 'help' in optmap:
            print(
                "usage: bucket-list clean [options]",
                "\n  options:",
                "\n    --help   prints help"
                )
            print(
                "\nFor more details you can refer official documentation here:",
                "\nhttps://github.com/arpitbbhayani/bucket-list/wiki/clean"
                )
            return

        if speedyio.yesno('Do you really want to clean all data?', default=False):
            Provider.clean()
            speedyio.success("All data for provider cleaned.")
