"""
XmlListConfig and XmlDictConfig source: http://code.activestate.com/recipes/410469-xml-as-dictionary/
"""
from xml.etree import cElementTree

from .base import BaseLoader


class XmlLoader(BaseLoader):
    def parse(self, file: open) -> dict:
        root = cElementTree.XML(file.read())
        data = XmlDictConfig(root)
        return data


class XmlListConfig(list):
    def __init__(self, a_list):
        for element in a_list:
            if element:
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)


class XmlDictConfig(dict):
    """
    Example usage:

    >>> tree = ElementTree.parse('your_file.xml')
    >>> root = tree.getroot()
    >>> xmldict = XmlDictConfig(root)

    Or, if you want to use an XML string:

    >>> root = ElementTree.XML(xml_string)
    >>> xmldict = XmlDictConfig(root)

    And then use xmldict for what it is... a dict.
    """

    def __init__(self, parent_element):
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                # treat like dict - we assume that if the first two tags
                # in a series are different, then they are all different.
                if len(element) == 1 or element[0].tag != element[1].tag:
                    a_dict = XmlDictConfig(element)
                # treat like list - we assume that if the first two tags
                # in a series are the same, then the rest are the same.
                else:
                    # here, we put the list in dictionary; the key is the
                    # tag name the list elements all share in common, and
                    # the value is the list itself
                    a_dict = {element[0].tag: XmlListConfig(element)}
                # if the tag has attributes, add those to the dict
                if element.items():
                    a_dict.update(dict(element.items()))
                self.update({element.tag: a_dict})
            # this assumes that if you've got an attribute in a tag,
            # you won't be having any text. This may or may not be a
            # good idea -- time will tell. It works for the way we are
            # currently doing XML configuration files...
            # elif element.items():
            #     self.update({element.tag: dict(element.items())})
            # finally, if there are no child tags and no attributes, extract
            # the text
            else:
                element_type = element.attrib.get('type') or 'str'
                if element_type == 'int':
                    value = try_type(element.text, int)
                elif element_type == 'float':
                    value = try_type(element.text, float)
                elif element_type in ['bool', 'boolean']:
                    value = True if element.text.lower() in ['true', '1', '+', 'allow'] else False
                else:
                    value = element.text
                self.update({element.tag: value})


def try_type(text, result_type):
    try:
        return result_type(text)
    except:
        return text
