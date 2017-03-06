import click
from collections.abc import Mapping, Sequence
from collections import OrderedDict, defaultdict
import json
import os
import re
import sys

if sys.version_info[0] == 3 and sys.version_info[1] == 5:
    from math import gcd
else:
    from fractions import gcd

from .common.formatter import sort_atml3


@click.group()
@click.argument('input', type=click.File('r'))
@click.pass_obj
def analyze(obj, input):
    """
    analyze a directory of atml3 files
    """
    print(input.name)
    try:
        fcontents = json.load(input, encoding='utf-8',
                              object_hook=OrderedDict,
                              object_pairs_hook=OrderedDict)
        obj['input'] = fcontents
    except Exception as e:
        print(e)


@analyze.command()
@click.pass_obj
def show(obj):
    """
    merely print the contents of the dict
    """
    return
    print(json.dumps(obj['input'], indent=4))


@click.group(chain=True, invoke_without_command=True)
@click.argument('path', type=click.Path(exists=True))
@click.pass_context
def atml3file(ctx, path):
    ctx.obj = {}
    if not os.path.isdir(path):
        click.echo('{} is not a directory'.format(path), err=True)
        return
                    # click.echo('\n\n{}'.format(name))
                    # click.echo(json.dumps(fcontents, indent=4))


def atml3file_iter(path):
    for root, dirs, files in os.walk(path):
        for name in files:
            if name[-6:].lower() == '.atml3':
                fname = os.path.join(root, name)
                try:
                    with open(fname, 'r') as f:
                        fcontents = f.read()
                        atml3 = json.loads(fcontents, encoding='utf-8',
                                              object_hook=OrderedDict,
                                              object_pairs_hook=OrderedDict)
                        item = {
                            'fcontents': fcontents,
                            'atml3': atml3,
                            'filename': fname,
                        }
                        yield item
                except Exception as e:
                    item = {
                        'filename': fname,
                        'atml3': {},
                        'fcontents': '',
                        'error': str(e),
                    }
                    yield item


@atml3file.resultcallback()
def process_commands(processors, path):
    def echo_name(iterator):
        for item in iterator:
            click.echo(item['filename'])
            yield item

    iterator = atml3file_iter(path)
    # iterator = echo_name(iterator)
    for processor in processors:
        iterator = processor(iterator)
    for item in iterator:
        pass


@atml3file.command('collect-errors')
def atml3_errors():
    def processor(iterator):
        counter = 0
        fails = 0
        errors = []
        for item in iterator:
            counter += 1
            if 'error' in item:
                fails += 1
                errors.append('{}: {}'.format(item['filename'], item['error']))
            yield item
        click.echo('\n\n{}/{} failed to validate:'.format(fails, counter))
        click.echo('\n'.join(errors))
    return processor

@atml3file.command('keys')
@click.pass_obj
def atml3_rootkeys(obj):
    obj['allkeys'] = set()
    obj['orderings'] = set()
    def processor(iterator):
        for item in iterator:
            for key in item['atml3'].keys():
                obj['allkeys'].add(key)
            orderstring = '", "'.join(item['atml3'].keys())
            obj['orderings'].add('"{}"'.format(orderstring))
            yield item
        click.echo('\n')
        click.echo('all keys:\n"{}"'.format('", "'.join(obj['allkeys'])))
        click.echo('all orderings:')
        #print(obj['orderings'])
        orderings = list(obj['orderings'])
        orderings.sort()
        for line in orderings:
            click.echo(line)

    return processor

@atml3file.command('reindent')
def atml3_reindent():
    def processor(iterator):
        for item in iterator:
            if item.get('atml3', '') and item.get('filename', ''):
                filename = item['filename']
                atml3 = item['atml3']
                click.echo('writing reindented file to {}'.format(filename))
                with open(filename, 'w') as f:
                    json.dump(atml3, f, indent=2)
            yield item
    return processor

@atml3file.command('showkey')
@click.argument('key')
def atml3_print_keyvalue(key):
    def processor(iterator):
        for item in iterator:
            if key in item['atml3']:
                click.echo('{} {}: "{}"'.format(item['filename'], key, item['atml3'][key]))
            yield item

    return processor

@atml3file.command('sort')
def atml3_sort():
    def processor(iterator):
        for item in iterator:
            if item['atml3']:
                print(json.dumps(sort_atml3(item['atml3']), indent=2))
            yield item

    return processor


@atml3file.command('guess-indentation')
def atml3_guess_indentation():
    def processor(iterator):
        for item in iterator:
            if item['fcontents']:
                tabdivisor = 0
                spacedivisor = 0
                for line in item['fcontents'].split('\n'):
                    tabs = 0
                    spaces = 0
                    for letter in line:
                        if letter == ' ':
                            spaces += 1
                        elif letter == '\t':
                            tabs += 1
                        else:
                            break
                    tabdivisor = gcd(tabdivisor, tabs)
                    spacedivisor = gcd(spacedivisor, spaces)
                    # click.echo('{} tabs {} spaces'.format(tabs, spaces))
                if spacedivisor > 0:
                    click.echo('{}: {} spaces'.format(item['filename'], spacedivisor))
                elif tabdivisor > 0:
                    click.echo('{}: {} tabs'.format(item['filename'], tabdivisor))


            yield item

    return processor

class TypeSuggester(object):

    def __init__(self):
        self.suggestions = defaultdict(int)

    def suggest(self, typename):
        self.suggestions[typename] += 1

    def print_suggestions(self):
        d = self.suggestions
        total = sum(d.values())
        sorter = ((k, d[k]) for k in sorted(d, key=d.get, reverse=True))
        key, value = list(sorter)[0]
        print('{}% {}'.format(value / total * 100.0,
                              key))
        # for key, value in sorter:
        #     #print('{}% {}'.format(value / total * 100.0,
        #     #                      key))
        #     print('key', key)
        #     print('value', value)

    def highest_suggestion(self):
        d = self.suggestions
        total = sum(d.values())
        sorter = ((k, d[k]) for k in sorted(d, key=d.get, reverse=True))
        key, value = list(sorter)[0]
        return key


keys = defaultdict(TypeSuggester)

def analyze_key(key):
    if '.' in key:
        parts = key.split('.')

@atml3file.command('find-data')
def atml3_find_data():
    data_re = re.compile(r'\#[^) ,]+')
    def recurse_data(item, path):
        global keys
        if isinstance(item, str):
            if path.endswith('mappingExpression') or path.endswith('truthExpression'):
                variables = data_re.findall(item)
                if variables:
                    for key in variables:
                        if 'str({})'.format(key) in item:
                            keys[key].suggest('string')
                        elif 'numeric({})'.format(key) in item:
                            keys[key].suggest('string')
                        else:
                            #print(item)
                            keys
                    #print(path, variables)
                #print(path, item)
        elif isinstance(item, Mapping):
            for key, value in item.items():
                recurse_data(value,
                             '{}.{}'.format(path,
                                            key))
        elif isinstance(item, Sequence):
            for pos, element in enumerate(item):
                recurse_data(element,
                             '{}.{}'.format(path,
                                       pos))

    def processor(iterator):
        global keys
        for item in iterator:
            if item['atml3']:
                atml3 = item['atml3']
                recurse_data(atml3, '')
            yield item
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
            },
        }

        list_re = re.compile(r'\[\d+\]$')
        for key in sorted(keys.keys()):
            isarray = False
            if '.' in key:
                # print()
                prop = schema['properties']
                accessor = key.lstrip('#').split('.')
                for snippet in accessor:
                    match = list_re.search(snippet)
                    if match:
                        isarray = True
                        # is a list
                        key_without_index = snippet[:snippet.rfind('[')]
                        prop[key_without_index] = {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {}
                            }
                        }
                        prop = prop[key_without_index]['items']['properties']
                    else:
                        prop[snippet] = {
                            'type': 'object',
                            'properties': {}
                        }
                        prop = prop[snippet]['properties']
                if isarray:
                    print(json.dumps(schema, indent=2, sort_keys=True))
                        #print(key)
                    # prop[key] = {
                    #     'type': '
                    # }
                # print(accessor)
                # print(key)
                # keys[key].print_suggestions()
    return processor
