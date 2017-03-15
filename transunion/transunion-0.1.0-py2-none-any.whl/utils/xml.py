from __future__ import absolute_import

from collections import OrderedDict
from xml.sax.saxutils import XMLGenerator

from defusedxml import ElementTree as etree
from six import StringIO


def loads(string):
    tree = etree.fromstring(string)
    root = _clean_tag(tree.tag)
    data = _xml_convert(tree)

    return {root: data}


def dumps(dictionary):
    if dictionary is None:
        return ''

    stream = StringIO()

    xml = XMLGenerator(stream, 'utf-8')

    xml.startDocument()
    _dict_to_xml(xml, dictionary)
    xml.endDocument()

    return stream.getvalue()


def _dict_to_xml(xml, data):
    if isinstance(data, dict):
        for key, value in data.items():
            if not isinstance(value, list):
                value = [value]
            for _val in value:
                attr, val = _get_attr(_val)
                xml.startElement(key, attrs=attr)
                _dict_to_xml(xml, val)
                xml.endElement(key)
    elif data is not None:
        xml.characters(str(data))


def _get_attr(value):
    attr, val = OrderedDict(), None
    if isinstance(value, dict):
        for _key in value:
            if is_attribute(_key):
                keyword = _key[2:-2]
                if keyword == 'val':
                    val = value[_key]
                else:
                    attr[_key[2:-2]] = value[_key]
        value = {k: value[k] for k in value if not is_attribute(k)}
    if val is None:
        val = value
    return attr, val


def is_attribute(key):
    return key.startswith('__') and key.endswith('__')


def _xml_convert(element):
    children = list(element)
    if len(children) == 0:
        return _type_convert(element.text)
    else:
        data = {}
        for child in children:
            clean_tag = _clean_tag(child.tag)
            if clean_tag in data:
                if isinstance(data[clean_tag], list):
                    data[clean_tag].append(_xml_convert(child))
                else:
                    data[clean_tag] = [data[clean_tag]] + [_xml_convert(child)]
            else:
                data[_clean_tag(child.tag)] = _xml_convert(child)
        return data


def _type_convert(value):
    if value is None:
        return value

    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        return value


def _clean_tag(tag):
    """remove namespace in the tag"""
    return tag.split("}")[1][:] if "}" in tag else tag
