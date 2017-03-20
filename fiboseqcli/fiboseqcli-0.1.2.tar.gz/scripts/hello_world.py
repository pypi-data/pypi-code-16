import click


@click.command()
@click.option('--count', default=1, help='Number of greetings.')
@click.argument('name', nargs=-1)
def hello(count, name):
    """
    Name: Hello\n
    Description: Say Hi\n
    Arguments:\n
        - NAME:\n
          - Everyone you want to greet.\n
          - Takes multiple strings, i.e. "Jane" "John"
    """
    for n in name:
        for x in range(count):
            click.echo('Hello %s!' % n)
