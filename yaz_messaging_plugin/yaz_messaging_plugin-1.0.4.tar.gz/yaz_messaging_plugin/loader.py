import collections
import yaml
import yaml.constructor


class OrderedDictLoader(yaml.SafeLoader):
    """
    A YAML loader that loads mappings into ordered dictionaries.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # The types below are part of the yaml language, see http://yaml.org/type/
        self.add_constructor(u'tag:yaml.org,2002:map', type(self).construct_yaml_map)
        self.add_constructor(u'tag:yaml.org,2002:omap', type(self).construct_yaml_map)
        self.add_constructor(u'tag:yaml.org,2002:bool', type(self).add_string)
        self.add_constructor(u'tag:yaml.org,2002:float', type(self).add_string)
        self.add_constructor(u'tag:yaml.org,2002:int', type(self).add_string)
        self.add_constructor(u'tag:yaml.org,2002:null', type(self).add_string)
        self.add_constructor(u'tag:yaml.org,2002:timestamp', type(self).add_string)

    def construct_yaml_map(self, node):
        data = collections.OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            raise yaml.constructor.ConstructorError(None, None,
                                                    'expected a mapping node, but found %s' % node.id, node.start_mark)

        mapping = collections.OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError as exc:
                raise yaml.constructor.ConstructorError('while constructing a mapping',
                                                        node.start_mark, 'found unacceptable key (%s)' % exc, key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping

    def add_string(self, node):
        """We do not want YAML 1.1 scalar types to be evaluated"""
        return self.construct_scalar(node)
