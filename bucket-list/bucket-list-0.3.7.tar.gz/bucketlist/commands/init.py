import getopt
from bucketlist import configio
from bucketlist import appconfig, speedyio
from bucketlist.errors import BucketlistError
from bucketlist.providers import get_current_provider


class InitCommand:
    __command_name__ = 'init'

    def execute(self, argv):
        Provider = get_current_provider()

        optlist, args = getopt.getopt(argv, '', ['help'])
        optmap = {
            opt[0].lstrip('-'): opt[1]
            for opt in optlist
        }

        if 'help' in optmap:
            print(
                "usage: bucket-list init [options]",
                "\n  options:",
                "\n    --help   prints help"
                )
            print(
                "\nFor more details you can refer official documentation here:",
                "\nhttps://github.com/arpitbbhayani/bucket-list/wiki/init"
                )
            return

        old_config = appconfig.get_all('provider_config')

        appconfig.delete_section('provider_config')
        appconfig.create_section('provider_config')

        provider_name = appconfig.get_provider_name()
        provider_config = configio.get_provider_config(provider_name)

        if provider_config is None:
            speedyio.error("Unsupported provider '{}'".format(provider_name))
            return

        for config_name in provider_config:
            default_value = old_config.get(config_name)
            value = speedyio.askfor(config_name, empty_allowed=False,
                                    default=default_value)
            appconfig.put('provider_config', config_name, value)

        Provider.init()
        speedyio.success("Provider {} initialized".format(provider_name))
