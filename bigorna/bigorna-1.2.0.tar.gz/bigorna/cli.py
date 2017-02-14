import sys

import click

from bigorna import __VERSION__
from bigorna.commons import Config, setup_logging
from bigorna.core import Bigorna, Standalone
from bigorna.tracker import JobTracker


pass_config = click.make_pass_decorator(Config)


@click.group()
@click.version_option(version=__VERSION__)
@click.option('--log', default=None,
              help="Log destination file path")
@click.option('--config', default='config.yml', type=click.Path(),
              help="Configuration file path")
@click.pass_context
def main(ctx, config, log):
    cfg = Config(config)
    click.secho("Loading configuration from file %s" % config, fg='green')
    setup_logging(log)
    ctx.obj = cfg


@main.command(help="Run http server")
@click.option('--debug', is_flag=True,
              help="Run server on debug mode")
@pass_config
def runserver(cfg, debug):
    from bigorna.http import app
    app.cfg = cfg
    app.bigorna = Bigorna.new(cfg)
    app.run(host="0.0.0.0", port=cfg.http_port, debug=debug)


@main.command(help="""
    Execute a task in standalone mode. Standalone tasks are not saved on Bigorna's database.
    You should provide application params like 'param=value'
""")
@click.argument('task_type', required=True)
@click.argument('params', required=False, nargs=-1)
@pass_config
def execute(cfg, task_type, params):
    try:
        def extract(param):
            tks = param.split('=')
            return (tks[0], tks[1])
        if params:
            params = dict(map(extract, params))
        else:
            params = {}
    except:
        click.secho("Wrong parameters format, it should be 'param1=value1 param2=value2'",
                    fg='red')
        return

    click.secho("Executing %s with params %s" % (task_type, params), fg='green')
    bigorna = Standalone.new(cfg)

    try:
        bigorna.submit(task_type, params)
    except (TypeError, KeyError) as e:
        click.secho("Missing parameters for exec command: %s" % e, fg='red')

    success = bigorna.join()
    sys.exit(0 if success else 1)


@main.command(help="Creates database file")
@pass_config
def create_db(cfg):
    click.secho("Creating db on file %s" % cfg.db_file, fg='green')
    from bigorna.tracker.persistence import Base, create_engine
    Base.metadata.create_all(create_engine(cfg))


@main.command(help="""Force mark all Running and Pending jobs as failed.
This command should be used only in case of a crash, to put the db to a consistent state.""")
@pass_config
def force_fail(cfg):
    tracker = JobTracker(cfg)
    count = tracker.force_fail()
    click.secho("%s jobs marked as failed!" % count, fg='red')
