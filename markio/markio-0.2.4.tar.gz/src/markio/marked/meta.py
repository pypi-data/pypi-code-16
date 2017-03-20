import collections

from markio.utils import load_yaml, dump_yaml


class Meta(collections.MutableMapping):
    """
    Base class for the .meta attribute of a Marked AST.

    Behaves like a dictionary with case-insensitive keys.
    """
    _default = {
        'author': None,
        'Author': None,
        'slug': None,
        'Slug': None,
    }

    @property
    def tags(self):
        return list(self['tags'])

    def __init__(self, document, data, casefold=True):
        self.document = document
        self._keytrans = lambda x: x.casefold() if casefold else lambda x: x
        self._data = collections.OrderedDict()
        self._keymap = {'tags': 'Tags'}

        if isinstance(data, str):
            self.from_string(data)
        else:
            D = collections.OrderedDict(data)
            self.update(D)

    def __getitem__(self, key):
        key = self._keytrans(key)
        key = self._keymap.get(key, key)

        try:
            return self._data[key]
        except KeyError:
            if key in ['tags', 'Tags']:
                self._data[key] = value = []
                return value
            return self._default[key]

    def __setitem__(self, key, value):
        if key in ['tags', 'Tags']:
            self._settags(value)
            return

        # Key already exists in dictionary
        if key in self._data:
            self._data[key] = value
            return

        # A transformed version of key exists
        if key in self._keymap:
            key = self._keymap[key]
            self._data[key] = value
            return

        # The key nor a transformed version exists
        key_trans = self._keytrans(key)
        self._keymap[key_trans] = key
        self._data[key] = value

    def __delitem__(self, key):
        raise KeyError(key)

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __str__(self):
        items = collections.OrderedDict(self._data)
        tags = items.pop('tags', None)
        if tags is None:
            tags = items.pop('Tags', None)
        data = dump_yaml(items, pretty=True)
        if tags:
            data += 'Tags: %s' % (', '.join(self.tags))
        return data

    def _settags(self, value):
        if isinstance(value, str):
            value = [x.strip() for x in value.split(',')]
        value = list(value)
        self._data['Tags'] = value

    def from_string(self, data):
        """
        Load meta information from a string of YAML data.
        """

        for k, v in load_yaml(data).items():
            self[k] = v

    def add_tag(self, tag):
        """
        Add a tag to meta information
        """

        if tag not in self['tags']:
            self['tags'].append(tag)

    def add_tags(self, *args):
        """
        Add a list of tags.
        """

        if len(args) == 1 and isinstance(args[0], (list, tuple, set)):
            args = args[0]

        for tag in args:
            self.add_tag(tag)

    def remove_tag(self, tag):
        """
        Discard tag.
        """

        if tag in self['tags']:
            self['tags'].remove(tag)

    def to_json(self):
        """
        Convert meta to a JSON-compatible dict of meta information
        """

        data = {self._keytrans(k): v for (k, v) in self._data.items()}
        if self.tags:
            data['tags'] = self.tags
        else:
            data.pop('tags', None)
        return data


def meta_property(name, default=None):
    """
    A property that maps into a meta key.
    """

    def fget(self):
        return self.meta.get(name, default)

    def fset(self, value):
        self.meta[name] = value

    return property(fget, fset)
