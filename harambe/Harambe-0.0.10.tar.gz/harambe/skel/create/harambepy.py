"""
________________________________________________________________________________


 /$$   /$$                                            /$$
| $$  | $$                                           | $$
| $$  | $$  /$$$$$$   /$$$$$$  /$$$$$$  /$$$$$$/$$$$ | $$$$$$$   /$$$$$$
| $$$$$$$$ |____  $$ /$$__  $$|____  $$| $$_  $$_  $$| $$__  $$ /$$__  $$
| $$__  $$  /$$$$$$$| $$  \__/ /$$$$$$$| $$ \ $$ \ $$| $$  \ $$| $$$$$$$$
| $$  | $$ /$$__  $$| $$      /$$__  $$| $$ | $$ | $$| $$  | $$| $$_____/
| $$  | $$|  $$$$$$$| $$     |  $$$$$$$| $$ | $$ | $$| $$$$$$$/|  $$$$$$$
|__/  |__/ \_______/|__/      \_______/|__/ |__/ |__/|_______/  \_______/



https://github.com/mardix/harambe

________________________________________________________________________________
"""

from harambe import GoHarambe

# Init Harambe
# The 'app' variable is required for the CLI tool, which is accessed at `harambe`
app = GoHarambe(__name__)

# ------------------------------------------------------------------------------
# CLI

from harambe.cli import CLI

class MyCli(CLI):
    def __init__(self, command, click):
        """
        Initiate the command line
        Place all your command functions in this method
        And they can be called with

            > harambe $fn_name

        ie:

            @command
            def hello():
                click.echo("Hello World!")

        In your terminal:
            > harambe hello


        :param command: copy of the cli.command
        :param click: click
        """

        @command()
        def setup():
            """
            The setup
            """
            click.echo("This is a setup!")