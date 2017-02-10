"""The dynamodb tool provides the ``put`` task.

The ``put`` task is used to upload json files to DynamoDB tables.  The
files to upload, and the target tables are specified in the project
configuration under the ``dynamodb`` key.

The ``targets`` sub-key, contains a mapping of name to configuration,
where each specifies ``source``, ``args``, ``table``, ``values`` and
``descrypt`` keys.


Source
------

The ``source`` key specifies a pattern to match the source files to
upload.


Table
-----

The ``table`` key specifies the table name to upload to.  Each source
file is uploaded independently to the table.

The table value is a python format string that may contain
interpolations for the args and values specified below.


Arguments
---------

A directory target can be configured with ``args``, a list containing
the names of values it expects to be passed on the command line.


Values
------

The ``values`` key configures a list of names for values to be added
to the top level of the JSON before upload.

``values`` can contain names from ``args`` and the following:

project        the name of the project
branch         the current branch name
branch-slug    the current branch name, sanitised
sha            the current commit sha as a hex string
sha-mod-1024   the current as a decimal modulo 1024

The ``values`` list can also contain items of the form ``name=value``,
which will pass the var ``name`` to terraform, with the value
calculated according to ``value`` from the list above.


Decrypt
-------

The ``decrypt`` key specifies that the files matched by ``source``
should first be decrypted.  The value of the key specifies an
environment variable that holds the decryption key.

"""
import argparse
import logging

from menhir.tool import Tool
from menhir.utils import multi, method
from menhir.tool_utils import OK, FAIL, NOTHING_TO_DO

log = logging.getLogger(__name__)

REMOVE_SUBS_RE = r'%\([\w_]+\)s'


def tool():
    return DynamoDB()


class DynamoDB(Tool):

    def dir_info(tool, path, info):
        """Does a glob match on the source patterns.

        This will not be 100% accurate, but will not give false
        negatives.
        """
        import re
        from glob import glob
        from os.path import join
        files = None
        targets = info.get('dynamodb', {}).get('targets')
        if targets:
            for k, v in targets.items():
                source = v.get('source', 'config.*.json')
                source = re.sub(REMOVE_SUBS_RE, '*', source)
                files = glob(join(path, source))
        return {
            'project_recognised': False,
            'can_run': bool(files),
        }

    def dependencies(tool, path):
        return []

    def arg_parser(tool, **kwargs):
        return parser(**kwargs)

    def execute_tool(tool, path, info, args,):
        """Execute a build phase."""
        return task(path, info, args)


def parser(**kwargs):
    parser = argparse.ArgumentParser(
        description="Commands to upload JSON to dynamodb table.",
        **kwargs
    )
    parsers = parser.add_subparsers(help="DynamoDB commands", dest='phase')
    p = parsers.add_parser(
        'put',
        help='Put JSON files to dynamodb'
    )
    p.add_argument('target', nargs=1)
    p.add_argument('args', nargs="*")
    return parser


@multi
def task(path, info, args):
    return args.phase


@method(task, 'put')
def task_put(path, info, args):
    if not (
            'changed' not in info or
            info['changed'].get('self') or
            info['changed'].get('dependents')
    ):
        return NOTHING_TO_DO
    config = info.get('config', {}).get('dynamodb', {})
    targets = config.get('targets', {})
    target = args.target[0]
    spec = targets.get(target)
    print('config', config, 'targets', targets)
    print('target', target, 'spec', spec)
    if spec is None:
        return NOTHING_TO_DO

    res = put(path, info, target, args.args, spec)
    if res != OK:
        return res
    return OK


def put(path, info, target, args, spec):
    from glob import glob
    from os import getenv
    from os.path import join
    import boto3
    from menhir.tool_config import aliased_value_array

    print('put')
    args_names = spec.get('args', [])
    args_dict = dict(zip(args_names, args))

    values = spec.get('values', [])
    values_map = {
        k: v for k, v in aliased_value_array(values, info, path, args_dict)
    }

    values_and_args = args_dict.copy()
    values_and_args.update(values_map)

    source = spec.get('source', 'config.json')
    source = source % values_and_args

    table_name = spec.get('table', 'config.%(project)s')
    table_name = table_name % values_and_args

    decrypt = spec.get('decrypt')
    if decrypt:
        decrypt = getenv(decrypt)
        if not decrypt:
            log.error(
                'Decryption key %s specified, but not present',
                spec.get('decrypt')
            )
            return FAIL

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    files = glob(join(path, source))

    print('files', files)
    if not files:
        log.error(
            'No files match %(source)s for target %(target)s',
            {'source': source, 'target': target}
        )
        return FAIL

    for file in files:
        log.info('Uploading %s to %s', file, table_name)
        put_file(table, values_map, file, decrypt)

    return OK


def put_file(table, values_map, file, decrypt):
    from json import loads
    from menhir.fileutils import load_json, load_encrypted

    if decrypt:
        s = load_encrypted(file, decrypt)
        data = loads(s)
    else:
        data = load_json(file)
    data.update(values_map)
    log.info('Uploading %s', data)

    table.put_item(Item=data)
