''' module supporting yaml-format configuration files '''
# copyright (c) 2017, Edward F. Wahl.

from bunch import Bunch
import os.path
import six
import yaml

from . import Preprocessor

def unbunchify_tree(tree):
    '''
    convenience function to traverse a tree of dicts, lists
    and turn all dicts it contains to bunches

    safer than bunch.unbunchify as it doesn't mangle custom classes
    '''
    if isinstance(tree, dict):
        if type(tree) == Bunch:
            tree = dict((k, unbunchify_tree(v)) for k,v in six.iteritems(tree))
        else:
            for key, value in six.iteritems(tree):
                tree[key] = unbunchify_tree(value)
    elif isinstance(tree, (list, tuple)):
        return type(tree)( unbunchify_tree(v) for v in tree)
    return tree

def bunchify_tree(tree):
    '''
    convenience function to traverse a tree of dicts, lists
    and turn all dicts it contains to bunches

    safer than bunch.bunchify as it doesn't mangle custom classes
    '''
    if isinstance(tree, dict):
        # only change real dicts to bunch, not derived classes
        # that may have other puposes
        if type(tree) == dict:
            tree = Bunch(tree)
        for item in tree:
            tree[item] = bunchify_tree(tree[item])
    elif isinstance(tree, (list, tuple)):
        tree = type(tree)(bunchify_tree(v) for v in tree)

    return tree

def load(yaml_data, **kwargs):
    ''' convert yaml data into a configuration
         @param yaml_data: yaml data to be parsed
         @param configData: do substitution from this data

         parsing includes two custom yaml tags

         !format does string.format substitution using mapping data in
         the node. kwargs override default values if present
    '''

    def _python_format(loader, node):
        ''' do python string formatting

            requires a mapping input
            special key "format" is the string to be formatted
            all other keys are passed as keyword arguments
        '''

        params = Bunch(loader.construct_mapping(node))

        # allow kwargs substitution
        for key, value in kwargs.items():
            if key in params:
                params[key] = value

        rv = params.format.format(**params) #pylint: disable=W0142
        return rv

    yaml.add_constructor('!format', _python_format)

    return bunchify_tree(yaml.load(yaml_data))

def load_file(path, **kwargs):
    ''' convert yaml data into a configuration
         @param path: path to file to be parsed
         @return:

         wrapper around the config_to_yaml function
         see details of that function for operation
    '''

    data = Preprocessor.Run(sourcefile = os.path.expanduser(path))
    return load(data, **kwargs)

