from collections import OrderedDict
from coreapi.document import Link

from . import helpers


def get_spore_method_name(keys: list, action: str) -> str:
    """

    TODO: better annotations in python3.6
    TODO: enhance name of func. not optimal yet !
    """
    if not keys:
        return action

    object_name = ''.join(reversed(keys))
    if action in ('list', ):
        if not object_name.endswith('s'):
            object_name = object_name + 's'
    elif object_name.endswith('s'):
        object_name = object_name.rstrip('s')
    return '{}_{}'.format(action, object_name)


def build_method_from_link(link: Link, formats: list) -> OrderedDict:
    method_attributes = [
        ('path', link.url),
        ('method', link.action),
        ('required_params', [
            field.name for field in link.fields
            if field.required and field.location in ('path', 'query')
        ]),
        ('optional_params', [
            field.name for field in link.fields
            if not field.required and field.location == 'query'
        ]),
        ('payload_required', link.action in ('post', 'put', 'patch'))
    ]

    if getattr(link, 'encoding', ''):
        method_attributes.append(('payload_format', link.encoding))

    # TODO: enhance this part
    if set(formats) != set(link.formats):
        method_attributes.append(('formats', link.formats))

    method_attributes.extend([
        ('authentication', link.authentication),
        ('documentation', link.description)
    ])

    return OrderedDict(method_attributes)


def get_spore_methods_from_document(node, keys=(), formats=()):
    links = []

    for key, child in getattr(node, 'data', {}).items():
        index = keys + (key, )
        links.extend(get_spore_methods_from_document(child, index, formats))

    for action, link in getattr(node, 'links', {}).items():
        links.append((
            get_spore_method_name(keys, action),
            build_method_from_link(link, formats)
        ))

    return links


def generate_spore_object(document, global_formats, spore_settings):
    """
    TODO: spore settings definition and integration
    """

    methods = get_spore_methods_from_document(document, (), global_formats)

    spore = OrderedDict()
    spore["name"] = document.title
    spore["base_url"] = document.url
    spore["version"] = ''
    spore["formats"] = global_formats
    spore["methods"] = OrderedDict(methods)
    spore["authority"] = ''
    spore["meta"] = {
        "authors": [],
        "documentation": document.description
    }

    return spore
