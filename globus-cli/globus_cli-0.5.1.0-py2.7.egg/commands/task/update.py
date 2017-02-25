import click

from globus_cli.safeio import safeprint
from globus_cli.parsing import common_options, task_id_arg
from globus_cli.helpers import outformat_is_json, print_json_response

from globus_cli.services.transfer import get_client, assemble_generic_doc


@click.command('update', short_help='Update a Task',
               help='Update label and/or deadline on an active Task')
@common_options
@task_id_arg
@click.option('--label', help='New Label for the Task')
@click.option('--deadline', help='New Deadline for the Task')
def update_task(deadline, label, task_id):
    """
    Executor for `globus task update`
    """
    client = get_client()

    task_doc = assemble_generic_doc(
        'task', label=label, deadline=deadline)

    res = client.update_task(task_id, task_doc)

    if outformat_is_json():
        print_json_response(res)
    else:
        safeprint('Success')
