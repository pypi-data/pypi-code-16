import asyncio
import click
import os
import string
import sys
import uuid
import yaml
import json
from asyncio.subprocess import PIPE
from datetime import datetime

@asyncio.coroutine
def dup_stream(stream, *output):
    while True:
        line = yield from stream.readline()
        if not line:
            break
        for f in output:
            f.write(line) # assume it doesn't block
    return  

@asyncio.coroutine
def log_cmd(cmd, stdout, stderr):
    # start process
    process = yield from asyncio.create_subprocess_shell(cmd,
            stdout=PIPE, stderr=PIPE)

    # read child's stdout/stderr concurrently (capture and duplicate)
    try:
        yield from asyncio.gather(
            dup_stream(process.stdout, *stdout),
            dup_stream(process.stderr, *stderr))
    except Exception:
        process.kill()
        raise
    finally:
        # wait for the process to exit
        rc = yield from process.wait()
    return rc


def execute(name, cmd, log=None, quiet=False):
    stdout  = []
    stderr = []
    if not quiet:
        click.secho(cmd, fg='green')
        stdout.append(sys.stdout.buffer)
        stderr.append(sys.stderr.buffer)
    if log is not None:
        if not os.path.isdir(log):
            os.makedirs(log)
        uid = uuid.uuid4().hex
        metadata = {"name": name,
                    "cmd": cmd,
                    "uid": uid,
                    "type": "shell",
                    "status": "started",
                    "returncode": None,
                    "start_time": datetime.now().isoformat(),
                    "end_time": None}
        json.dump(metadata, open(os.path.join(log, "{}-meta.txt".format(uid)), "w"), indent=2)
        stdout.append(open(os.path.join(log, "{}-stdout.txt".format(uid)), "wb"))
        stderr.append(open(os.path.join(log, "{}-stderr.txt".format(uid)), "wb"))
    try:        
        loop = asyncio.get_event_loop()
        rc = loop.run_until_complete(log_cmd(cmd, stdout, stderr))
        loop.close()
        status = "success" if rc == 0 else "failed"
    except:
        rc = None
        status = "error"
        raise
    finally:
        for f in stdout+stderr:
            f.close()

    if log is not None:
        metadata["returncode"] = rc
        metadata["status"] = status
        metadata["end_time"] = datetime.now().isoformat()
        json.dump(metadata, open(os.path.join(log, "{}-meta.txt".format(uid)), "w"), indent=2)
    return rc

def get_params(s):
    formatter = string.Formatter()
    return [fname for _, fname, _, _ in formatter.parse(s) if fname]

try:
    config = yaml.load(open(os.path.join(os.getcwd(), "bud.yml")))
except FileNotFoundError:
    config = {}


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
                params.append(click.Option(("--{}".format(p),), envvar=p.upper(), default=default))
            else:
                params.append(click.Option(("--{}".format(p),), envvar=p.upper(), required=True))

        def callback(*args, **kwargs):
            sys.exit(execute(name, task.format(**kwargs), log=ctx.obj["log"], quiet=ctx.obj["quiet"]))

        ret = click.Command(name, help=task, short_help=task, params=params, callback=callback)
        return ret


@click.command(cls=BudCLI, invoke_without_command=True)
@click.option('--log', help='logdir')
@click.option('--quiet', is_flag=True, default=False, help='logdir')
@click.pass_context
def cli(ctx, log, quiet):
    """simple command executor"""
    ctx.obj["log"] = log
    ctx.obj["quiet"] = quiet 

def main():
    cli(obj={})


if __name__ == '__main__':
    main() 

