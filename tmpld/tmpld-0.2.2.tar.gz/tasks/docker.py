import os

from invoke import task


@task(default=True)
def build(ctx, tag=None):
    ctx.run("docker build -t %s --force-rm ." % tag or ctx.docker.tag)
