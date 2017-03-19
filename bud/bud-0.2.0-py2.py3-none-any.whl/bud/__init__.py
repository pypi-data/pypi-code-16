import click
import os
import yaml
import string
import uuid
import datetime
from datetime import datetime
import subprocess
import sys
from subprocess import Popen, PIPE, STDOUT


def get_params(s):
    formatter = string.Formatter()
    return [fname for _, fname, _, _ in formatter.parse(s) if fname]

def execute(cmd):
    click.secho(cmd, fg='green')
    subprocess.call(cmd, shell=True)

config = yaml.load(open(os.path.join(os.getcwd(), "bud.yml")))

class BudCLI(click.MultiCommand):


    def list_commands(self, ctx):
        return list(config.get("tasks", {}).keys())

    def get_command(self, ctx, name):
        ns = {}
        task =  config.get("tasks", {})[name]
        params = []
        for p in get_params(task):
            default = config.get("vars", {}).get(p, None)
            if default:
                params.append(click.Option(("--{}".format(p),), envvar=p.upper(), default=default, required=True))
            else:
                params.append(click.Option(("--{}".format(p),), envvar=p.upper(), required=True))

        @click.pass_context
        def callback(*args, **kwargs):
            execute(task.format(**kwargs))

        ret = click.Command(name, help=task, short_help=task, params=params, callback=callback)
        return ret


@click.command(cls=BudCLI, invoke_without_command=True)
@click.option('--log', help='logdir')
@click.pass_context
def cli(ctx, log, config):
    """simple command executor"""
    ctx.obj["log"] = log

def main():
    cli(obj={})


if __name__ == '__main__':
    main() 

