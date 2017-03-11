import click

from prompt_toolkit import prompt


@click.group()
def main():
    pass


@click.command()
def add():
    tool = prompt(u"Adding a tool, eh? What's it called?")
    print('You said: %s' % tool)


main.add_command(add)
