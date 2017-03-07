"""
XmlToDict
"""
import collections
import re
class XmlToDict(object):
    """Convert an xml element to a python dict.
    >>> python_dict = XmlToDict().element_to_dict(xml_element)
    """
    def __init__(self,
            attrib_prefix='_',
            text_key='_text_',
            namespace_pattern=r'\{.*\}',
            namespace_replace='',
            ):
        """
        attrib_prefix       - prepend this to each tag attribute name
        text_key            - the key to store the tag's text in
        namespace_pattern   - a regular expression used to match a
                              tagname's namespace
        namespace_replace   - a replacement string (which may contain
                              back references to match groups in the
                              namespace_pattern)
        """
        self.attrib_prefix = attrib_prefix
        self.text_key = text_key
        self.namespace_pattern = re.compile(namespace_pattern)
        self.namespace_replace = namespace_replace

    def element_to_dict(self, x):
        """convert ``x`` to a dict.
        ``x`` - an xml element.
        """
        tag = self.fix_tag(x.tag)
        d = {tag: {}}
        children = list(x)
        if x.attrib:
            d[tag].update(
                (self.attrib_prefix + self.fix_tag(k), v)
                    for k, v in x.attrib.items())
        if x.text and x.text.strip():
            if children or x.attrib:
                d[tag][self.text_key] = x.text
            else:
                d[tag] = x.text
        if children:
            dd = collections.defaultdict(list)
            for dc in [self.element_to_dict(c) for c in children]:
                for k, v in dc.items():
                    dd[self.fix_tag(k)].append(v)
            d[tag].update(
                {self.fix_tag(k): v[0] if len(v) == 1 else v
                    for k, v in dd.items()})
        return d

    def fix_tag(self, tag):
        """replace namespace_pattern in ``tag`` with namespace_replace
        """
        return self.namespace_pattern.sub(self.namespace_replace, tag)

