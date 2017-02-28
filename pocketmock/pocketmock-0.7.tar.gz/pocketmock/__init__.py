import re
from collections import namedtuple
from unittest.mock import MagicMock
from dill.source import getsource


def create_mock_object(class_):
    methods = fetch_methods(class_)
    instance_variables = fetch_instance_variables(class_)

    all_attributes = methods.union(instance_variables)

    mock_object = namedtuple('MockObject', all_attributes)

    for method in methods:
        setattr(mock_object, method, MagicMock())
    
    for instance_variable in instance_variables:
        setattr(mock_object, instance_variable, None)

    return mock_object


def fetch_methods(class_):
    attributes = dir(class_)
    methods = filter(
        lambda attribute: _is_public_method(class_, attribute),
        attributes)
    return set(methods)


def fetch_instance_variables(class_):
    try:
        constructor_text = getsource(class_.__init__)
        all_instance_variables = map(
            lambda match: match[5:-1].strip(),
            _raw_instance_variables(constructor_text)
        )
        instance_variables = filter(
            lambda instance_variable: _is_public(instance_variable),
            all_instance_variables
        )
        return set(instance_variables)
    except TypeError:
        return set() 

def _raw_instance_variables(constructor_text):
    pattern = re.compile(r'\bself\.(?:[a-zA-Z_]+)(?:[a-zA-Z_1-9]*)[ ]*=')
    return pattern.findall(constructor_text)



def _is_public_method(class_, attribute):
    return _is_function(class_, attribute) and _is_public(attribute)


def _is_function(class_, attribute):
    return callable(getattr(class_, attribute))


def _is_public(attribute):
    return not attribute.startswith('_')

