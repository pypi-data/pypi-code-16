import click
import scripts.hello_world as hel


@click.group()
def cli():
    pass


@click.command()
@click.option('--num', default=10, prompt='Sequence iterations.', help='Number of iterations for the Fibonacci '
                                                                       'sequence.')
def fibo(num):
    """
    Name: Fibonacci sequence\n
    Description: Displays an n amount of Fibonacci iterations.
    """
    n = int(num)
    l = [0, 1]
    if n == 0:
        result = l[0]
    elif n == 1:
        result = l
    a = 0
    b = 1
    for i in range(0, n-1):
        b += a
        a = b - a
        l.append(b)
    result = l

    click.echo(result)


cli.add_command(fibo)
cli.add_command(hel.hello)

if __name__ == '__main__':
    fibo()
