import click


@click.group('set', chain=True)
@pass_data
def setdefault(data):
    pass


@setdefault.command()
@click.argument('token')
@pass_data
def auth_token(data, token):
    if token:
        data.auth_token = token


@setdefault.command()
@pass_data
def print_token(data):
        print(token)
