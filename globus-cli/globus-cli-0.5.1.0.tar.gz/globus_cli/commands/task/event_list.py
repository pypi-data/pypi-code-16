import click

from globus_cli.parsing import common_options, task_id_arg
from globus_cli.helpers import outformat_is_json, print_table

from globus_cli.services.transfer import print_json_from_iterator, get_client


@click.command('event-list', help='List Events for a given Task')
@common_options
@task_id_arg
def task_event_list(task_id):
    """
    Executor for `globus task-event-list`
    """
    client = get_client()

    event_iterator = client.task_event_list(task_id)

    if outformat_is_json():
        print_json_from_iterator(event_iterator)
    else:
        print_table(event_iterator, [
            ('Time', 'time'), ('Code', 'code'), ('Is Error', 'is_error'),
            ('Details', 'details')])
