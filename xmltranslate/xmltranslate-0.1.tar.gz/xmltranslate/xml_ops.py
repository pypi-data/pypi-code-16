from xml.etree.ElementTree import fromstring, Element, SubElement, dump


def xml2dict(xml_obj: str):
    tree = fromstring(xml_obj)
    return _xml2dict(tree)


def dict2xml(dict_obj: dict):
    for key, value in dict_obj.items():
        xml_ele = Element(key)
        return dump(_dict2xml(value, xml_ele))


def _dict2xml(dict_obj: dict, root):
    for key, value in dict_obj.items():
        if type(value) == dict:
            t = SubElement(root, key)
            _dict2xml(value, t)
        else:
            t = SubElement(root, key)
            t.text = value
    return root


def _xml2dict(xml_ele):
    if xml_ele.getchildren():
        obj = dict()
        for child in xml_ele.getchildren():
            obj[child.tag] = _xml2dict(child)
        return {
            xml_ele.tag: obj
        }
    else:
        return xml_ele.text

if __name__ == '__main__':
    test_string = '<parent><child2>CHILD2</child2><child1><child11>CHILD11</child11></child1></parent>'
    test_obj = {
        'parent': {
            'child1': {
                'child11': 'CHILD11'
            },
            'child2': 'CHILD2'
        }
    }
    #print(xml2dict(test_string))
    #print(dict2xml(test_obj))
