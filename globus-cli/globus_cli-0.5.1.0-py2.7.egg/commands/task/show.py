import click

from globus_cli.parsing import common_options, task_id_arg
from globus_cli.helpers import (
    outformat_is_json, print_json_response, colon_formatted_print)

from globus_cli.services.transfer import get_client


COMMON_FIELDS = [
    ('Label', 'label'),
    ('Task ID', 'task_id'),
    ('Type', 'type'),
    ('Directories', 'directories'),
    ('Files', 'files'),
    ('Status', 'status'),
    ('Request Time', 'request_time'),
]

ACTIVE_FIELDS = [
    ('Deadline', 'deadline'),
    ('Details', 'nice_status'),
]

COMPLETED_FIELDS = [
    ('Completion Time', 'completion_time'),
]

DELETE_FIELDS = [
    ('Endpoint', 'source_endpoint_display_name'),
]

TRANSFER_FIELDS = [
    ('Source Endpoint', 'source_endpoint_display_name'),
    ('Destination Endpoint', 'destination_endpoint_display_name'),
]


@click.command('show', help='Show detailed information about a specific Task')
@common_options
@task_id_arg
def show_task(task_id):
    """
    Executor for `globus task show`
    """
    client = get_client()

    res = client.get_task(task_id)

    if outformat_is_json():
        print_json_response(res)
    else:
        fields = COMMON_FIELDS + \
            (COMPLETED_FIELDS if res['completion_time'] else ACTIVE_FIELDS) + \
            (DELETE_FIELDS if res['type'] == 'DELETE' else TRANSFER_FIELDS)
        colon_formatted_print(res, fields)
