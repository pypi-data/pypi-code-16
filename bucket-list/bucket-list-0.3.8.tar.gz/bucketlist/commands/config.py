import os
import json
import getopt

from bucketlist import appconfig, speedyio, SUPPORTED_PROVIDERS
from bucketlist.errors import BucketlistError


class ConfigCommand:
    __command_name__ = 'config'

    def execute(self, argv):
        optlist, args = getopt.getopt(argv, '', ['set=', 'get=', 'set-provider=', 'help'])
        optmap = {
            opt[0].lstrip('-'): opt[1]
            for opt in optlist
        }

        if 'help' in optmap:
            print(
                "usage: bucket-list config [options]",
                "\n  options:",
                "\n    --get            prints value of config set in your config file",
                "\n    --set            sets value for config in your config file",
                "\n    --set-provider   change your provider",
                "\n    --help           prints help"
                )
            print(
                "\nFor more details you can refer official documentation here:",
                "\nhttps://github.com/arpitbbhayani/bucket-list/wiki/config"
                )
            return

        if 'set-provider' in optmap:
            if optmap['set-provider'] not in SUPPORTED_PROVIDERS:
                raise BucketlistError("Unsupported provider '{}'".format(optmap['set-provider']))

            appconfig.put('provider', 'name', optmap['set-provider'])

            appconfig.init(optmap['set-provider'])
            speedyio.info("Since you changed the provider. You must run `bucket-list init`.")

        elif 'set' in optmap:
            if len(args) == 0:
                raise BucketlistError("Value for config '{}' not provided.".format(optmap['set']))

            config_name = optmap['set']
            if config_name == 'provider.name':
                raise BucketlistError("You cannot change provider name like this.\n" +
                                      "In case you want to change the provider please run following command.\n" +
                                      "    bucket-list config --set-provider <provider_name>")

            tokens = config_name.split('.')
            if len(tokens) != 2:
                raise BucketlistError("Invalid config '{}'.".format(optmap['set']))

            appconfig.put(tokens[0], tokens[1], args[0])

            if tokens[0] == 'provider_config':
                speedyio.info("Since you changed the config oy your provider. You must run `bucket-list init`.")

        elif 'get' in optmap:
            config_name = optmap['get']

            tokens = config_name.split('.')
            if len(tokens) != 2:
                raise BucketlistError("Invalid config '{}'".format(config_name))

            speedyio.plain_print(appconfig.get(tokens[0], tokens[1]))
