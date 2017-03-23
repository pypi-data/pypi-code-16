import json
import click

from globus_cli.safeio import safeprint
from globus_cli.parsing import common_options, task_id_arg
from globus_cli.helpers import outformat_is_json, print_json_response

from globus_cli.services.transfer import get_client


@click.command('cancel', short_help='Cancel a Task',
               help='Cancel a Task owned by the current user')
@common_options
@task_id_arg(required=False)
@click.option('--all', '-a', is_flag=True,
              help='Cancel all in-progress tasks that you own')
def cancel_task(all, task_id):
    """
    Executor for `globus task cancel`
    """

    if bool(all) + bool(task_id) != 1:
        raise click.UsageError('You must pass EITHER the special --all flag '
                               'to cancel all in-progress tasks OR a single '
                               'task ID to cancel.')

    client = get_client()

    if all:
        from sys import maxsize
        task_ids = [
            task_row['task_id']
            for task_row in client.task_list(
                filter='type:TRANSFER,DELETE/status:ACTIVE,INACTIVE',
                fields='task_id',
                num_results=maxsize,  # FIXME want to ask for "unlimited" set
            )
        ]

        if not task_ids:
            raise click.ClickException('You have no in-progress tasks.')

        if outformat_is_json():
            safeprint(json.dumps(
                {
                    'results': [client.cancel_task(i).data for i in task_ids],
                    'task_ids': task_ids,
                },
                indent=2,
            ))

        else:
            task_count = len(task_ids)
            safeprint('Canceling all tasks ({} total)...'.format(task_count))
            for task_number, task_id in enumerate(task_ids, start=1):
                safeprint('{} ({} of {}): {}'.
                          format(task_id, task_number, task_count,
                                 client.cancel_task(task_id)['message']))

    else:
        res = client.cancel_task(task_id)

        if outformat_is_json():
            print_json_response(res)
        else:
            safeprint(res['message'])
