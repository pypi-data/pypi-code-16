import click
from collections import OrderedDict
from collections.abc import Mapping, Sequence


ROOT_ORDERING=[
    'version',
    'name',
    'training_sha',
    'errors',
    'requirementLevels',

    'properties',
    'productTypes',

    'sentences',
    'lookups',
    'sentenceGroups',

    'product_types',
    'billigstesRemapping',
]


def _sort_recurse(item):
    if isinstance(item, str):
        result = item
    elif isinstance(item, Mapping):
        result = OrderedDict()
        for key in sorted(item.keys()):
            result[key] = _sort_recurse(item[key])
    elif isinstance(item, Sequence):
        result = list()
        for element in item:
            result.append(_sort_recurse(element))
    else:
        result = item
    return result


def sort_atml3(atml3):
    result = OrderedDict()
    for key in ROOT_ORDERING:
        result[key] =  None
    for key in atml3:
        result[key] = _sort_recurse(atml3[key])
    empty = []
    for key in result:
        if result[key] is None:
            empty.append(key)
    for key in empty:
        del result[key]
    return result


def heading(headline):
    click.secho(headline, bold=True)
    click.secho('='*len(headline), bold=True)


def pretty_print_object(obj, headline=None):
    if headline:
        heading(headline)
    for key, value in obj.items():
        print('{}: {}'.format(key, value))
