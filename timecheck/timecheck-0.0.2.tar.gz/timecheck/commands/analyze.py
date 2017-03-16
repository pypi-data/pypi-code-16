import getopt

from timecheck.analyzer import analyze


class AnalyzeCommand:
    __command_name__ = 'analyze'

    def execute(self, argv):
        optlist, args = getopt.getopt(argv, 'f:', ['help'])
        optmap = {
            opt[0].lstrip('-'): opt[1]
            for opt in optlist
        }

        if 'help' in optmap:
            print(
                "usage: timecheck analyze -f <.tc file>",
                "\n  options:",
                "\n    -f       .tc file",
                "\n    --help   prints help"
                )
            return

        if 'f' not in optmap:
            print("For help, run: timecheck analyze --help")
            return

        analyze(optmap['f'])
