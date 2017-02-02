import getopt
from bucketlist import appconfig, speedyio
from bucketlist.providers import get_current_provider


class CleanCommand:
    __command_name__ = 'clean'

    def execute(self, argv):
        Provider = get_current_provider()

        optlist, args = getopt.getopt(argv, '', [])
        optmap = {
            opt[0].lstrip('-'):opt[1]
            for opt in optlist
        }

        if speedyio.yesno('Do you really want to clean all data?', default=False):
            Provider.clean()
            speedyio.success("All data for provider cleaned.")
