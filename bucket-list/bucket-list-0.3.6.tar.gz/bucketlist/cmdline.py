import sys
import getopt
import configparser

from bucketlist import speedyio, logger, appconfig
from bucketlist.commands import AddCommand
from bucketlist.commands import ViewCommand
from bucketlist.commands import MarkCommand
from bucketlist.commands import InitCommand
from bucketlist.commands import BackupCommand
from bucketlist.commands import ConfigCommand
from bucketlist.commands import RestoreCommand
from bucketlist.commands import CleanCommand
from bucketlist.errors import BucketlistError

commands = {
    AddCommand.__command_name__: AddCommand(),
    ViewCommand.__command_name__: ViewCommand(),
    MarkCommand.__command_name__: MarkCommand(),
    InitCommand.__command_name__: InitCommand(),
    BackupCommand.__command_name__: BackupCommand(),
    ConfigCommand.__command_name__: ConfigCommand(),
    RestoreCommand.__command_name__: RestoreCommand(),
    CleanCommand.__command_name__: CleanCommand()
}


def execute(argv=None, settings=None):
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) == 0:
        print(
            "usage: bucket-list <command> <args supported by commands>"
            )
        print(
            "\ncommands:",
            "\n  add:      The add command adds a new item in your bucket",
            "\n            list for a category.",
            "\n  backup:   The backup command takes a local backup of all",
            "\n            your items from your provider.",
            "\n  clean:    The clean command deletes all the data under",
            "\n            bucket-list and or created by bucket-list from",
            "\n            your current provider.",
            "\n  config:   The config command is used get and set various",
            "\n            configuration values and customizations.",
            "\n  init:     The init command reads the preferred provider name",
            "\n            and initialises it."
            "\n  mark:     The mark command marks an item in your bucket",
            "\n            list as completed.",
            "\n  restore:  The restore command takes your local backup",
            "\n            (create from backup command) and create corresponding",
            "\n            items in your current provider.",
            "\n  view:     The view command lists all items in your bucket",
            "\n            list for a category.",
            )
        print(
            "\nFor more details you can refer official documentation here:",
            "\nhttps://github.com/arpitbbhayani/bucket-list/wiki"
            )
        return

    command_str = argv.pop(0)
    command = commands.get(command_str)

    if command is None:
        speedyio.error("Invalid commmand {}".format(command_str))
        return

    try:
        command.execute(argv)
    except BucketlistError as e:
        speedyio.error("{}".format(e.description))
    except speedyio.SpeedyIOError as e:
        speedyio.error("{}".format(e.description))
    except getopt.GetoptError as e:
        speedyio.error(str(e))
    except configparser.NoOptionError as e:
        speedyio.error("Config '{}' under '{}' not set \u2639".format(e.option, e.section))
        speedyio.info("Run `bucket-list config --set {}.{} <value>`".format(e.section, e.option))
    except PermissionError as e:
        speedyio.error(str(e))
    except KeyboardInterrupt:
        speedyio.error("The process was killed \u2639")
    except Exception as e:
        logger.exception(e)
        speedyio.error("Something went really bad \u2639  Check the logs ({}) for more details."
                       .format(appconfig.get('logging', 'file')))
