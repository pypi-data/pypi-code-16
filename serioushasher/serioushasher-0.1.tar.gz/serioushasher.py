import click
import hashlib

@click.command()
@click.option('--round', '-r', default=1, help="The number of rounds you wish to hash the string for.")
@click.option('--value', '-v', default="", help="The string you wish to hash")
@click.option('--algorithm', '-a', default="md5", type=click.Choice(['md5', 'sha512']), help="What hash algorithm you wish to use, md5 or sha512")
@click.option('--salt', '-s', default="", help="The salt you wish to use")
@click.option('--position', '-p', default="f", type=click.Choice(['f', 'e']), help="Salt position, f(front) or e(end)")

def hash(round, value, algorithm, salt, position):
    hashed_value = value
    for i in range(round):
        hashed_value = salt_value(hashed_value, salt, position)
        if algorithm == "sha512":
            hashed_value = hashlib.sha512(hashed_value).hexdigest()
        elif algorithm == "md5":
            hashed_value = hashlib.md5(hashed_value).hexdigest()
    click.echo(hashed_value)

def salt_value(value, salt, position):
    hashed_pwd = value
    if position == "f":
        hashed_pwd = salt + hashed_pwd
    else:
        hashed_pwd += salt
    return hashed_pwd

if __name__ == '__main__':
    hash()