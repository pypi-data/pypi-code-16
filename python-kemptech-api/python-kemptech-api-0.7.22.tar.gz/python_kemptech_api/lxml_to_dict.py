from io import BytesIO
from collections import OrderedDict

from lxml import etree


class Stack:
    def __init__(self):
        self._storage = []

    def push(self, item):
        self._storage.append(item)

    def pop(self):
        return self._storage.pop()

    def peek(self):
        return self._storage[-1]


def process_element_text(text):
    # Default behaviour for xmltodict is to strip whitespace
    # and transform empty strings to None values
    return text.strip() or None \
        if text is not None \
        else None


def add_data_to_parent(tag, data, parent):
    """
    Add an item of data associated with a given XML tag to its parent.
    If the key already exists in the parent,
    the key will be transformed into a list and the data appended to it


    :param tag: The XML element tag associated with the data being inserted
    :param data: The data being added to the parent dictionary
    :param parent: The dictionary to inject data into
    """
    if tag in parent:
        existing_elem = parent[tag]
        if not isinstance(existing_elem, list):
            parent[tag] = [existing_elem]
        parent[tag].append(data)
    else:
        parent[tag] = data


def parse(xml, dict_factory=OrderedDict):
    """
    Convert a raw XML string into a Python dictionary.
    This function is designed to be compatible with
    the default behaviour of ``xmltodict.parse``,
    and should act as a drop-in replacement

    :param xml: A raw XML string to be parsed.
    :param dict_factory: Specifies what dictionary type should be used
                            for building the return value.
                            By default, ``OrderedDict`` is used to mimic
                            the behaviour of ``xmltodict``.
    :return: A dictionary containing the data from the XML string,
                using each element's name as the dictionary key.
                Elements with nested children or attributes are dictionaries,
                while plain-text elements are strings.
    """

    # Prepares a generator to iteratively step through the XML tree structure
    # to avoid incurring the memory overhead of loading the full XML tree
    # Only open/close tag events are required for preparing the dict
    xml_iter = etree.iterparse(
        BytesIO(xml.encode('utf-8')),
        events=('start', 'end'))

    parent_stack = Stack()
    parent = dict_factory()
    parent_stack.push(parent)
    for action, element in xml_iter:
        has_children = len(element)
        has_attribs = element.attrib
        if action == 'start':
            # Elements with nested nodes or attributes
            # become a dict instead of a plain str entry
            if has_attribs or has_children:
                parent = dict_factory()
                parent_stack.push(parent)
                for name, value in element.attrib.items():
                    parent['@' + name] = value

        if action == 'end':
            if has_children or has_attribs:
                current_element = parent
                parent_stack.pop()
                parent = parent_stack.peek()
                value = process_element_text(element.text)
                # xmltodict does not add None values to elements that have attributes
                if has_attribs and value is not None:
                    current_element['#text'] = value
                add_data_to_parent(element.tag, current_element, parent)
            elif not has_attribs:
                # Insert text entries into the parent dict
                # If an entry exists, transform to a collection
                # otherwise insert the text entry
                value = process_element_text(element.text)
                add_data_to_parent(element.tag, value, parent)
    return parent
