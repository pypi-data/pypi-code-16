import click

from globus_cli.safeio import safeprint
from globus_cli.parsing import common_options
from globus_cli.helpers import outformat_is_json, print_json_response

from globus_cli.services.transfer import get_client


@click.command('generate-submission-id', short_help='Get a submission ID',
               help=("Generate a new Task submission ID for use in "
                     "`globus transfer` and `gloubs delete`. Submission IDs "
                     "allow you to safely retry submission of a Task in the "
                     "presence of network errors. No matter how many times "
                     "you submit a Task with a given ID, it will only be "
                     "accepted and executed once. The response status may "
                     "change between submissions."))
@common_options
def generate_submission_id():
    """
    Executor for `globus task generate-submission-id`
    """
    client = get_client()

    res = client.get_submission_id()

    if outformat_is_json():
        print_json_response(res)
    else:
        safeprint(res['value'])
