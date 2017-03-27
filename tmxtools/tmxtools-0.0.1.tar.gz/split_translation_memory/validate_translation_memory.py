
import os
import xml.etree.ElementTree as ElementTree
HEAD = 0
BODY = 1

def is_tmx_valid(filepath):
    return filepath_exists(filepath)  and has_header_and_body(filepath) and only_contains_tu_elements(filepath)

def filepath_exists(filepath):
    return os.path.exists(filepath)

def has_header_and_body(filepath):
    tree = ElementTree.parse(filepath)
    root = tree.getroot()
    if len(root) != 2:
        return False
    if root[HEAD].tag != 'header':
        return False
    if root[BODY].tag != 'body':
        return False
    return True

def only_contains_tu_elements(filepath):
    tree = ElementTree.parse(filepath)
    root = tree.getroot()
    for element in root[BODY]:
        if element.tag != 'tu':
            return False
    return True



if __name__ == "__main__":
    is_tmx_valid('testfile.tmx')
    #is_tmx_valid('country_data.xml')
