"""
xml2py
"""
import xml.etree.cElementTree
from .xmltodict import XmlToDict
from .dotdict import DotDict

__all__ = [
        'DotDict',
        'XmlToDict',
        'dict_load', 'dict_loads',
        'dotdict_load', 'dotdict_loads',
        'to_dotdict',
        'to_list',
        ]

def dict_load(xml_filename, **kwargs):
    """ converts xml file to dict.
    ``xml_filename`` -  the name of the xml file or the file object
                        to convert.
    ``kwargs`` - keyword arguments are passed to XmlToDict.__init__
    """
    tree = xml.etree.cElementTree.parse(xml_filename)
    root = tree.getroot()
    return XmlToDict(**kwargs).element_to_dict(root)

def dict_loads(xml_string, **kwargs):
    """ converts ``xml_string`` to dict.
    ``kwargs`` - keyword arguments are passed to XmlToDict.__init__
    """
    root = xml.etree.cElementTree.fromstring(xml_string)
    return XmlToDict(**kwargs).element_to_dict(root)

def dotdict_load(xml_filename, **kwargs):
    """ converts xml file to DotDict instance.
    ``xml_filename`` -  the name of the xml file or the file object
                        to convert.
    ``kwargs`` - keyword arguments are passed to dict_load
    """
    d = dict_load(xml_filename, **kwargs)
    return DotDict(d)

def dotdict_loads(xml_string, **kwargs):
    """ converts ``xml_string`` to DotDict instance.
    ``kwargs`` - keyword arguments are passed to dict_load
    """
    d = dict_loads(xml_string, **kwargs)
    return DotDict(d)

to_dotdict = DotDict.to_dotdict # pylint: disable=invalid-name

def to_list(obj, key=None):
    """ to_list(obj) returns obj if obj is a list, else [obj, ].
    to_list(obj, key) returns to_list(obj[key]) if key is in obj,
    else [].
    """
    if key is None:
        return obj if isinstance(obj, list) else [obj]
    else:
        return to_list(obj[key]) if key in obj else []

