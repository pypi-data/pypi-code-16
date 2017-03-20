import imp
import importlib
import os
import pkgutil
import sys
from importlib import import_module

MODULE_EXTENSIONS = ('.py', '.pyc', '.pyo')


def package_contents(package_name):
    file, pathname, description = imp.find_module(package_name)
    if file:
        raise ImportError('Not a package: %r', package_name)
    # Use a set because some may be both source and compiled.
    return set([os.path.splitext(module)[0]
                for module in os.listdir(pathname)
                if module.endswith(MODULE_EXTENSIONS)])


def get_all_subclasses(base, part, target):
    package = import_module(base + '.' + part)
    modules = package_contents(os.path.join(os.path.dirname(package.__path__[0]), part))
    sub_module_base_name = package.__package__ + '.'

    for module_obj in modules:
        if module_obj.startswith('__'):
            continue
        child_module = import_module(sub_module_base_name + module_obj)
        for attr in dir(child_module):
            try:
                attribute = getattr(child_module, attr)
                if issubclass(attribute, target):
                    if attribute is not target:
                        yield child_module
            except:
                continue


def import_submodules(package_name: str, ignore_names: list or tuple = None):
    """ Import all submodules of a module, recursively

    :param package_name: Package name
    :param ignore_names: skip submodules if name in skip
    :type package_name: str
    :type ignore_names: list or tuple
    :rtype: dict[types.ModuleType]
    """
    if ignore_names is None:
        ignore_names = []
    package = sys.modules[package_name]
    return {
        name: importlib.import_module(package_name + '.' + name)
        for loader, name, is_pkg in pkgutil.walk_packages(package.__path__)
        if name not in ignore_names
        }


def list_submodules(package_name, ignore_names=None):
    if ignore_names is None:
        ignore_names = []
    package = sys.modules[package_name]
    return tuple(
        name
        for loader, name, is_pkg in pkgutil.walk_packages(package.__path__)
        if name not in ignore_names)


def path_from_module(module):
    """Attempt to determine app's filesystem path from its module."""
    # See #21874 for extended discussion of the behavior of this method in
    # various cases.
    # Convert paths to list because Python 3's _NamespacePath does not
    # support indexing.
    paths = list(getattr(module, '__path__', []))
    if len(paths) != 1:
        filename = getattr(module, '__file__', None)
        if filename is not None:
            paths = [os.path.dirname(filename)]
        else:
            # For unknown reasons, sometimes the list returned by __path__
            # contains duplicates that must be removed (#25246).
            paths = list(set(paths))
    if len(paths) > 1:
        raise RuntimeError(
            "The app module %r has multiple filesystem locations (%r); "
            "you must configure this app with an AppConfig subclass "
            "with a 'path' class attribute." % (module, paths))
    elif not paths:
        raise RuntimeError(
            "The app module %r has no filesystem location, "
            "you must configure this app with an AppConfig subclass "
            "with a 'path' class attribute." % (module,))
    return paths[0]


def import_attr(package, attr):
    module = import_module(package)
    return getattr(module, attr)


def base_name(package):
    return '.'.join(package.split('.')[:-1])


def join(package, *submodules):
    return '.'.join([package, *submodules])


def split_package(package):
    if '.' not in package:
        raise IndexError('Nothing to split')
    package, _, module = package.rpartition('.')
    return package, module
