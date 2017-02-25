import click

from globus_cli.parsing import common_options, task_id_arg
from globus_cli.helpers import print_json_response

from globus_cli.services.transfer.helpers import get_client


@click.command('pause-info',
               help=('Show detailed info about pause rules that '
                     'are applied to a Task'))
@common_options
@task_id_arg
def task_pause_info(task_id):
    """
    Executor for `globus transfer task pause-info`
    """
    client = get_client()

    res = client.task_pause_info(task_id)

    print_json_response(res)
