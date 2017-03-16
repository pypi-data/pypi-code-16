# Source based on pyaml with a few modifications
import functools
import io
import operator as op
import string
import sys
import yaml
from collections import defaultdict, OrderedDict

from decimal import Decimal


class PrettyYAMLDumper(yaml.dumper.SafeDumper):
    def __init__(self, *args, **kwargs):
        self.pyaml_force_embed = kwargs.pop('force_embed', False)
        self.pyaml_string_val_style = kwargs.pop('string_val_style', None)
        super().__init__(*args, **kwargs)

    def represent_decimal(self, data):
        if data != data:
            value = '.nan'
        elif data == self.inf_value:
            value = '.inf'
        elif data == -self.inf_value:
            value = '-.inf'
        else:
            value = str(data).lower()
            if '.' not in value and 'e' in value:
                value = value.replace('e', '.0e', 1)
        return self.represent_scalar('tag:yaml.org,2002:float', value)

    def represent_odict(self, data):
        value = []
        node = yaml.nodes.MappingNode('tag:yaml.org,2002:map',
                                      value,
                                      flow_style=None)

        if self.alias_key is not None:
            self.represented_objects[self.alias_key] = node

        for item_key, item_value in data.items():
            node_key = self.represent_data(item_key)
            node_value = self.represent_data(item_value)
            value.append((node_key, node_value))

        node.flow_style = False
        return node

    def represent_undefined(self, data):
        if isinstance(data, tuple) and \
                data.__class__.__name__.startswith('namedtuple_'):
            return self.represent_odict(data._asdict())
        elif isinstance(data, OrderedDict):
            return self.represent_odict(data)
        elif isinstance(data, dict):
            return self.represent_dict(data)
        elif isinstance(data, Decimal):
            return self.represent_decimal(data)
        return super(PrettyYAMLDumper, self).represent_undefined(data)

    def serialize_node(self, node, parent, index):
        if self.pyaml_force_embed:
            self.serialized_nodes.clear()
        return super().serialize_node(node, parent, index)

    def pyaml_transliterate(self, st):
        from unidecode import unidecode
        valid = string.ascii_letters + string.digits + '-_'
        chars = [(c if c in valid else '_') for c in unidecode(st)]
        return ''.join(chars).lower()

    def anchor_node(self, node, hint=list()):
        if node in self.anchors:
            if self.anchors[node] is None and not self.pyaml_force_embed:
                if not hint:
                    data = self.generate_anchor(node)
                else:
                    values = '_-_'.join(map(op.attrgetter('value'), hint))
                    data = '{}'.format(self.pyaml_transliterate(values))
                self.anchors[node] = data
        else:
            self.anchors[node] = None
            if isinstance(node, yaml.nodes.SequenceNode):
                for item in node.value:
                    self.anchor_node(item)
            elif isinstance(node, yaml.nodes.MappingNode):
                for key, value in node.value:
                    self.anchor_node(key)
                    self.anchor_node(value, hint=hint + [key])


PrettyYAMLDumper.add_representer(defaultdict, PrettyYAMLDumper.represent_dict)
PrettyYAMLDumper.add_representer(OrderedDict, PrettyYAMLDumper.represent_odict)
PrettyYAMLDumper.add_representer(set, PrettyYAMLDumper.represent_list)
PrettyYAMLDumper.add_representer(None, PrettyYAMLDumper.represent_undefined)


class UnsafePrettyYAMLDumper(PrettyYAMLDumper):
    def expect_block_sequence(self):
        self.increase_indent(flow=False, indentless=False)
        self.state = self.expect_first_block_sequence_item

    def expect_block_sequence_item(self, first=False):
        if not first and isinstance(self.event, yaml.events.SequenceEndEvent):
            self.indent = self.indents.pop()
            self.state = self.states.pop()
        else:
            self.write_indent()
            self.write_indicator('-', True, indention=True)
            self.states.append(self.expect_block_sequence_item)
            self.expect_node(sequence=True)

    def choose_scalar_style(self):
        is_dict_key = self.states[-1] == self.expect_block_mapping_simple_value
        if is_dict_key:
            # Don't mess-up (replace) styles for dict keys, if possible
            if self.pyaml_string_val_style:
                self.event.style = 'plain'
        else:
            # Make sure we don't create "key: null" mapping accidentally
            if self.event.value.endswith(':'):
                self.event.style = "'"

        if self.event.style != 'plain' or not self.event.tag.endswith(':str'):
            return super().choose_scalar_style()

        # Choose the most human-readable valid scalar style
        value = self.event.value
        default_style = super().choose_scalar_style()
        if not value:
            return default_style
        if value[0] in '?-:' and (len(value) == 1 or value[1].isspace()):
            return default_style
        if value[0] in ' []{}, # &!* |> "\' % @':
            return default_style
        if ': ' in value or ' #' in value:
            return default_style

        return None

    def represent_stringish(self, data):
        # Will crash on bytestrings with weird chars in them, because we can't
        # tell if it's supposed to be e.g. utf-8 readable string or an
        # arbitrary binary buffer, and former one *must* be pretty-printed
        # PyYAML's Representer.represent_str does the guesswork and !!binary or
        # !!python/str. Explicit crash on any bytes object might be more sane,
        # but also annoying. Use something like base64 to encode such buffer
        # values instead. Having such binary stuff pretty much everywhere on
        # unix (e.g. paths) kinda sucks
        data = str(data)  # read the comment above

        # Try to use '|' style for multiline data,
        #  quoting it with 'literal' if lines are too long anyway,
        #  not sure if Emitter.analyze_scalar can also provide useful info here
        style = self.pyaml_string_val_style
        if not style:
            style = 'plain'
            if '\n' in data or (data and data[0] in '!&*['):
                style = 'literal'
                if '\n' in data[:-1]:
                    for line in data.splitlines():
                        if len(line) > self.best_width: break
                    else:
                        style = '|'

        return yaml.representer.ScalarNode('tag:yaml.org,2002:str', data,
                                           style=style)


for str_type in {bytes, str}:
    UnsafePrettyYAMLDumper.add_representer(
        str_type, UnsafePrettyYAMLDumper.represent_stringish)

UnsafePrettyYAMLDumper.add_representer(
    type(None), lambda s, o: s.represent_scalar('tag:yaml.org,2002:null', ''))


def add_representer(*args, **kws):
    PrettyYAMLDumper.add_representer(*args, **kws)
    UnsafePrettyYAMLDumper.add_representer(*args, **kws)


def dump_add_vspacing(buff, vspacing):
    """
    Post-processing to add some nice-ish spacing for deeper map/list levels.'
    """

    if isinstance(vspacing, int):
        vspacing = ['\n'] * (vspacing + 1)
    buff.seek(0)
    result = list()
    for line in buff:
        level = 0
        line = line.decode('utf-8')
        result.append(line)
        if ':' in line:
            while line.startswith('  '):
                level, line = level + 1, line[2:]
            if len(vspacing) > level and len(result) != 1:
                vspace = vspacing[level]
                if isinstance(vspace, int):
                    vspace = '\n' * vspace
                result.insert(-1, vspace)
    buff.seek(0), buff.truncate()
    buff.write(''.join(result).encode('utf-8'))


def dump(data, dest=str, safe=False,
         force_embed=False, vspacing=None, string_val_style=None, **kwargs):
    buff = io.BytesIO()
    Dumper = PrettyYAMLDumper if safe else UnsafePrettyYAMLDumper
    Dumper = functools.partial(Dumper,
                               force_embed=force_embed,
                               string_val_style=string_val_style)
    yaml.dump_all([data], buff,
                  Dumper=Dumper,
                  default_flow_style=False,
                  allow_unicode=True,
                  encoding='utf-8', **kwargs)

    if vspacing is not None:
        dump_add_vspacing(buff, vspacing)

    buff = buff.getvalue()

    if dest is bytes:
        return buff
    elif dest is str:
        return buff.decode('utf-8')
    else:
        try:
            dest.write(b'')  # tests if dst is str- or bytestream
        except:
            dest.write(buff.decode('utf-8'))
        else:
            dest.write(buff)


def pprint(*data, **kwargs):
    dst = kwargs.pop('file', kwargs.pop('dest', sys.stdout))
    if len(data) == 1:
        data, = data
    dump(data, dest=dst, **kwargs)

