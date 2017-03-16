import sys
import getopt

from timecheck.commands import AnalyzeCommand

commands = {
    AnalyzeCommand.__command_name__: AnalyzeCommand(),
}


def execute(argv=None, settings=None):
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) == 0:
        print(
            "usage: timecheck <command> <args supported by commands>"
            )
        print(
            "\ncommands:",
            "\n  analyze   Analyzes .tc files",
            "\n  visualize Visualizes the analysis in terms of graphs",
            "\n            and charts.",
            )
        return

    command_str = argv.pop(0)
    command = commands.get(command_str)

    if command is None:
        print("Invalid commmand {}".format(command_str))
        return

    try:
        command.execute(argv)
    except getopt.GetoptError as e:
        print(str(e))
