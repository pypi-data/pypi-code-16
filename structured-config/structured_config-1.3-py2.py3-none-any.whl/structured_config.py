__author__ = "Andrew Leech"
__copyright__ = "Copyright 2017, alelec"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Andrew Leech"
__email__ = "andrew@alelec.net"

import os
import sys
import yaml
import wrapt
import inspect


class ConfigFile(object):
    def __init__(self, config_path, config):
        """
        Config file container.
        :param str config_path: path to file for storage. Either absolute
                                 or relative to application. If relative,
                                 frozen status of application is observed
                                 for correct path determination
        :param Structure config: top level config item
        """
        self.write_enabled = False
        self.config_path = config_path
        # convert passed in config to a registered instance
        self.config = self.register_structure(config)
        assert isinstance(self.config, (config, type(config)))

        if not os.path.isabs(self.config_path):
            if getattr(sys, 'frozen', False):
                # running in a bundle
                appdir = os.path.dirname(sys.executable)
            else:
                # running live
                appdir = os.path.dirname(__file__)

            self.config_path = os.path.join(appdir, self.config_path)

        ## Startup
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as configfile:
                self.config = self.register_structure(yaml.load(configfile))

        self.write_enabled = True

        # Ensure the config file exists for new installations.
        if not os.path.exists(self.config_path):
            self.write_yaml()

    def write_yaml(self):
        if self.write_enabled:
            try:
                os.makedirs(os.path.dirname(self.config_path))
            except OSError:
                pass
            with open(self.config_path, 'w') as configfile:
                yaml.dump(self.config, configfile, default_flow_style=False)

    def register_structure(self, structure):
        """
        This will attach this config files' writer to the structure
        :param Structure structure: key to register
        :returns: structure as passed in
        """
        def attach(_structure):
            if inspect.isclass(_structure) and issubclass(_structure, Structure):
                _structure = _structure()
            if isinstance(_structure, Structure):
                _structure.register_config_file(self)

            return _structure

        structure = attach(structure)

        for key, val in structure:
            if isinstance(val, dict):
                for k, v in val.items():
                    val[k] = attach(v)

            elif isinstance(val, (list, set, tuple)):
                val = List((attach(v) for v in val))
                val.register_config_file(self)

            else:
                val = attach(val)
            structure[key] = val

        return structure


class Structure(object):
    def __init__(self, **kwargs):
        cls = self.__class__
        # Set the yaml name of the class
        self._yaml_tag = '!' + cls.__name__
        self._config_file = None  # type: ConfigFile

        # Ensure instance has copy of attributes from class
        self.__dict__.update({k:v for k,v in cls.__dict__.items()
                              if not k.startswith('_')})

        self.__dict__.update(kwargs)

        yaml.add_constructor(self._yaml_tag, cls._from_yaml)
        yaml.add_representer(cls, self._to_yaml)


    @classmethod
    def _from_yaml(cls, loader, node):
        return loader.construct_yaml_object(node, cls)

    def _to_yaml(self, dumper, data):
        return dumper.represent_yaml_object(self._yaml_tag, data, self.__class__, flow_style=False)

    def register_config_file(self, config_file):
        self._config_file = config_file

    def __iter__(self):
        for key, val in self.__dict__.items():
            yield key, val

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, item, val):
        return self.__setattr__(item, val)

    def __setattr__(self, key, value):
        value = value.value if isinstance(value, TypedField) else value
        if not hasattr(self, key):
            changed = True
            super().__setattr__(key, value)
        else:
            try:
                current = self.__dict__[key]
            except KeyError:
                current = self.__getattribute__(key, raw=True)

            if isinstance(current, TypedField):
                current.converter(value)  # Ensure the value is valid
                changed = value != current
                current.value = value
            else:
                changed = not hasattr(self, key) or value != current
                super().__setattr__(key, value)

        # Write out the yaml on each attribute update
        if changed and not key.startswith('_') and self._config_file:
            self._config_file.write_yaml()

    def __getattribute__(self, item, raw=False):
        current = object.__getattribute__(self, item)
        if not raw and isinstance(current, TypedField):
            return current.converter(current.value)
        return current

    def __repr__(self):
        return "%s: %s" % (self.__class__.__name__, self.__dict__)

    def __eq__(self, other):
        if isinstance(other, Structure):
            other = other.__getstate__()
        return self.__getstate__() == other

    def __getstate__(self):
        return {key: val for key, val in self.__dict__.items() if not key.startswith('_')}


class List(list):
    """
    Overridden list to allow us to wrap functions for automatic write.
    This is required as we can't wrap/replace the builtin list functions
    """
    yaml_tag = '!list'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config_file = None  # type: ConfigFile

    def register_config_file(self, config_file):
        self._config_file = config_file
        wrapt.wrap_function_wrapper(self, 'clear', self.write_after)
        wrapt.wrap_function_wrapper(self, 'extend', self.write_after)
        wrapt.wrap_function_wrapper(self, 'pop', self.write_after)
        wrapt.wrap_function_wrapper(self, 'remove', self.write_after)
        wrapt.wrap_function_wrapper(self, 'append', self.write_after)
        wrapt.wrap_function_wrapper(self, 'insert', self.write_after)

    def write_after(self, wrapped, instance, args, kwargs):
        ret = wrapped(*args, **kwargs)
        if self._config_file:
            self._config_file.write_yaml()
        return ret

    def __getstate__(self):
        return list(self)


def list_rep(dumper, data):
    """
    Ensure pyyaml treats our list as a regular list
    """
    return dumper.represent_list(list(data))


yaml.add_representer(List, list_rep)


class TypedField(object):
    def __init__(self, value, converter):
        self.value = value
        self.converter = converter

        cls = self.__class__
        self._yaml_tag = '!' + cls.__name__

        yaml.add_constructor(self._yaml_tag, self._from_yaml)
        yaml.add_representer(cls, self._to_yaml)

    def __getstate__(self):
        return dict(value=self.value, converter=self.converter)

    def __setstate__(self, state):
        self.__dict__.update(state)

    @classmethod
    def _from_yaml(cls, loader, node):
        return loader.construct_yaml_object(node, cls)

    def _to_yaml(self, dumper, data):
        return dumper.represent_yaml_object(self._yaml_tag, data, self.__class__, flow_style=False)



class IntField(TypedField):
    def __init__(self, value):
        super(IntField, self).__init__(value, int)
