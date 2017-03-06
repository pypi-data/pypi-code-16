#!/usr/bin/env python3
import click
from collections.abc import Mapping, Sequence
import datetime
import json
import os
from os.path import dirname
from os.path import join as pjoin
import re
import stat
import sys

import axsemantics
from axsemantics import constants
from axsemantics_cli.mapping_helpers import *


class ImporterSettings:
    IMPORT_UNCONFIGURED = False
    MAPPING = {}
    EXPORT = False
    FORCE_MAPPING = False
    AXSEMANTICS_USER = ''
    AXSEMANTICS_PASSWORD = ''
    AXSEMANTICS_TOKEN = ''
    AXSEMANTICS_CONTENT_PROJECT = 4004


SETTINGS = ImporterSettings


def is_zipfile(filename):
    try:
        with open(filename, 'rb') as f:
            header = f.read(2)
            return header == b'PK'
    except:
        pass
    return False


class UnmappedFieldException(Exception):
    pass


def _map_field(data, key, value):
    # fixes datetime.datetime is not json serializable
    if isinstance(value, datetime.datetime):
        value = value.isoformat()
    if key in SETTINGS.MAPPING:
        mapped_key = SETTINGS.MAPPING[key]
        if isinstance(mapped_key, str):
            data[mapped_key] = value

        elif isinstance(mapped_key, list):
            try:
                data.update(mapped_key[0](field=value,
                                          key=key,
                                          **mapped_key[1],
                ))
            except:
                print('Failed to parse field {} with content {}.'.format(key, value))

    else:
        if SETTINGS.IMPORT_UNCONFIGURED:
            data[normalize_key(key)] = value
        if SETTINGS.FORCE_MAPPING:
            raise UnmappedFieldException(key)


def _parse_row(row):
    data = {}

    for xslx_key in row.keys():
        xslx_value = row[xslx_key]

        _map_field(data, xslx_key, xslx_value)
    return data


def render_script(**kwargs):
    scriptfile = pjoin(dirname(__file__),
                       'importer.out')
    with open(scriptfile, 'r') as infile:
        data = infile.read()
    for key, value in kwargs.items():
        data = data.replace('{{' + str(key) + '}}', str(value))
    return data


def make_executable(filename):
    st = os.stat(filename)
    os.chmod(filename, st.st_mode | stat.S_IEXEC)


@click.command('create-importer')
@click.argument('filename')
@click.option('--content-project', '-c', help='content project id for this importer', prompt='Content Project ID', type=int)
@click.pass_obj
def new_importer(obj, filename, content_project):
    """
    Create a new importer
    """
    import sys
    interpreter = str(sys.executable)
    if constants.API_TOKEN:
        authtoken = constants.API_TOKEN
        username = ''
        password = ''
    else:
        authtoken = ''
        username = obj['login']
        password = obj['password']
    data = render_script(executable=interpreter,
                         content_project=content_project,
                         authtoken=authtoken,
                         username=username,
                         password=password,
    )
    with open(filename, 'w') as f:
        f.write(data)
    make_executable(filename)
    click.echo('Successfully created new script {}'.format(filename))
    click.echo('you most likely want to edit the script first,')
    click.echo('especially the MAPPING setting needs to be adjusted to each importer')
    click.echo('you can use the parameter -p to test if your mapping expression works, -p will never insert data.\n')
    click.echo('run the script with the file to import as parameter.\n')
    click.echo('Examples:')
    click.echo('> {} mydata.json'.format(filename))
    click.echo('  import all entries from mydata.json')
    click.echo('> {} moredata.xlsx -p'.format(filename))
    click.echo('  print the data after applying the mapping, do not import. Use this to check if your mapping is correct')

@click.command()
@click.argument('filename')
@click.option('--pretend', '-p', help="don't actually import, print the data that would be sent to server", default=False)
@click.pass_context
def importer(ctx, filename, pretend):
    """
    AXSemantics Data Importer

    \b
    FILENAME: a file to import,
    valid input formats are xlsx or json (with a list of objects)
    """
    EXCEL_MODE = False
    JSON_MODE = False
    if not os.path.exists(filename):
        sys.exit('Could not find file {}.'.format(filename))
    if is_zipfile(filename) and filename.lower().endswith('.xlsx'):
        try:
            import pandas as pd
        except:
            sys.exit('please install pandas to be able to import excel files\n'
                     'to do this run\n'
                     '> pip install pandas')
        xlsx = pd.ExcelFile(filename)
        EXCEL_MODE = True
    else:
        try:
            with open(filename, 'r') as f:
                obj = json.load(f)
            JSON_MODE = True
        except json.JSONDecodeError as exc:
            sys.exit('error parsing json data: {}'.format(str(exc)))
        except:
            sys.exit('parsing json file {} failed'.format(filename))

    if EXCEL_MODE:
        data = []
        sheet = xlsx.parse(0)
        # replace float with value `nan` with none
        sheet_with_none = sheet.where((pd.notnull(sheet)), None)

        for index, row in sheet_with_none.iterrows():
            data.append(_parse_row(row))

        if pretend:
            print(data)
            sys.exit(0)
        if SETTINGS.EXPORT is True:
            json_name = re.sub(r'.xlsx', '.json', filename)
            with open(json_name, 'w') as f:
                json.dump(data, f)
            sys.exit(0)

    elif JSON_MODE:
        data = []
        if isinstance(obj, Mapping):
            obj = [obj]
        unmapped_keys = set()
        for item in obj:
            if item is None:
                continue
            row = {}
            for key in item.keys():
                try:
                    _map_field(row, key, item[key])
                except UnmappedFieldException as e:
                    unmapped_keys.add(e.args[0])
            data.append(row)
        if unmapped_keys:
            print('''\033[31m[!]\033[0m there were unmapped keys

please fill out and add the lines below to your importer's mapping
''')
            for key in unmapped_keys:
                print("        '{}': '',".format(key))
            print()
            sys.exit(1)
        if pretend:
            print(data)
            sys.exit(0)
    else:
        sys.exit('File was not loaded')

    if SETTINGS.AXSEMANTICS_TOKEN:
        constants.API_TOKEN = SETTINGS.AXSEMANTICS_TOKEN
    else:
        axsemantics.login_myax(SETTINGS.AXSEMANTICS_USER, SETTINGS.AXSEMANTICS_PASSWORD)
    for pure_data in data:
        try:
            thing = axsemantics.Thing(
                uid=pure_data['uid'],
                name=pure_data['name'],
                pure_data=pure_data,
                cp_id=SETTINGS.AXSEMANTICS_CONTENT_PROJECT,
            )
            thing.create(api_token=SETTINGS.AXSEMANTICS_TOKEN)
            print('.', end='')
            sys.stdout.flush()
        except KeyError as e:
            print('Could not create thing for data {}, missing key {}.'.format(pure_data, e))
        except axsemantics.APIError as e:
            message = '''An error occurred while saving thing {}.
                \nMethod: {}\nResource: {}\nPayload: {}\nResponse: {} {}\n'''
            print(message.format(thing,
                                 e.request.request.method,
                                 e.request.url,
                                 e.request.request.body,
                                 e.request.status_code,
                                 e.request.content))


def run_importer(settings):
    global SETTINGS
    SETTINGS = settings
    importer()
