import click
import six

from globus_cli.parsing import common_options, ISOTimeType
from globus_cli.helpers import outformat_is_json, print_table

from globus_cli.services.transfer import print_json_from_iterator, get_client


@click.command('list', help='List Tasks for the current user')
@common_options
@click.option(
    "--limit", default=10, show_default=True, help="Limit number of results.")
@click.option(
    "--filter-task-id", multiple=True, type=click.UUID,
    help="task UUID to filter by. This option can be used multiple times.")
@click.option(
    "--filter-type", type=click.Choice(["TRANSFER", "DELETE"]),
    help="Filter results to only TRANSFER or DELETE tasks.")
@click.option(
    "--filter-status", multiple=True,
    type=click.Choice(["ACTIVE", "INACTIVE", "FAILED", "SUCCEEDED"]),
    help=("Task status to filter results by. "
          "This option can be used multiple times."))
@click.option(
    "--filter-label", multiple=True,
    help=("Filter results to task whose label matches pattern. "
          "This option can be used multiple times."))
@click.option(
    "--filter-not-label", multiple=True,
    help=("Filter not results whose label matches pattern. "
          "This option can be used multiple times."))
@click.option(
    "--inexact / --exact", default=True,
    help=("Allows / disallows --filter-label and --filter-not-label to use"
          "* as a wild-card character and ignore case"))
@click.option(
    "--filter-requested-after", type=ISOTimeType(),
    help="Filter results to tasks that were requested after given time.")
@click.option(
    "--filter-requested-before", type=ISOTimeType(),
    help="Filter results to tasks that were requested before given time.")
@click.option(
    "--filter-completed-after", type=ISOTimeType(),
    help="Filter results to tasks that were completed after given time.")
@click.option(
    "--filter-completed-before", type=ISOTimeType(),
    help="Filter results to tasks that were completed before given time.")
def task_list(limit, filter_task_id, filter_status, filter_type,
              filter_label, filter_not_label, inexact,
              filter_requested_after, filter_requested_before,
              filter_completed_after, filter_completed_before):
    """
    Executor for `globus task-list`
    """

    def _process_filterval(prefix, value, default=None):
        if value:
            if isinstance(value, six.string_types):
                return "{}:{}/".format(prefix, value)
            return "{}:{}/".format(prefix, ",".join(str(x) for x in value))
        else:
            return default or ""

    # make filter string
    filter_string = ""
    filter_string += _process_filterval("task_id", filter_task_id)
    filter_string += _process_filterval("status", filter_status)
    filter_string += _process_filterval("type", filter_type,
                                        default="type:TRANSFER,DELETE/")

    # combine data into one list for easier processing
    if inexact:
        label_data = (["~" + s for s in filter_label] +
                      ["!~" + s for s in filter_not_label])
    else:
        label_data = (["=" + s for s in filter_label] +
                      ["!" + s for s in filter_not_label])
    filter_string += _process_filterval("label", label_data)

    filter_string += _process_filterval(
        "request_time", [(filter_requested_after or ""),
                         (filter_requested_before or "")])
    filter_string += _process_filterval(
        "completion_time", [(filter_completed_after or ""),
                            (filter_completed_before or "")])

    client = get_client()
    task_iterator = client.task_list(
        num_results=limit,
        filter=filter_string[:-1])  # ignore trailing /

    if outformat_is_json():
        print_json_from_iterator(task_iterator)
    else:
        print_table(task_iterator, [
            ('Task ID', 'task_id'), ('Status', 'status'), ('Type', 'type'),
            ('Source Display Name', 'source_endpoint_display_name'),
            ('Dest Display Name', 'destination_endpoint_display_name'),
            ('Label', 'label')])
