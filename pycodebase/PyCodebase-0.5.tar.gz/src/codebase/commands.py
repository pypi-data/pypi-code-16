import itertools
import sys

from . import formatters


def activity(client, opts):
    if opts.project:
        results = client.get_project_activity(opts.project)
    else:
        results = client.get_activity()

    results = itertools.islice(results, opts.limit)

    cls = formatters.get_formatter(opts.format)
    columns = ['timestamp', 'type', 'title']

    formatter = cls(columns, _format_activity, sys.stdout)
    formatter(results)


def _format_activity(record):
    return record
