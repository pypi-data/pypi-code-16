#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string


SEP = "____"
KLS_NAME_CHARSET = set(string.ascii_letters + string.digits)
VAR_NAME_CHARSET = set(string.ascii_lowercase + string.digits + "_")
VAR_FORBIDDEN_CHARSET = set(r"""~`!@#$%^&*()-+={}[]|\:;"'<,>.?/""" + string.ascii_uppercase)

def is_valid_class_name(name):
    try:
        assert name[0].isupper()
        assert len(set(name).difference(KLS_NAME_CHARSET)) == 0
        return True
    except:
        return False


def is_valid_variable_name(name):
    try:
        assert name[0].islower()
        assert SEP not in name
        assert len(set(name).difference(VAR_NAME_CHARSET)) == 0
        return True
    except:
        return False


def is_valid_surfix(name):
    try:
        assert SEP not in name
        assert len(VAR_FORBIDDEN_CHARSET.intersection(name)) == 0
        return True
    except:
        return False
    
    
def to_variable_name(cls_name):
    assert is_valid_class_name(cls_name)

    words = list()
    chunks = list()
    for char in cls_name:
        if char.isupper():
            words.append("".join(chunks))
            chunks = ["_", char.lower()]
        else:
            chunks.append(char)
    words.append("".join(chunks))
    return "".join(words)[1:]


def test_is_valid_class_name():
    for name in ["User", "MyClass", "TestCase"]:
        assert is_valid_class_name(name) is True

    for name in ["user", "My_Class", "testCase"]:
        assert is_valid_class_name(name) is False


def test_is_valid_variable_name():
    for name in ["name", "my_class", "num1"]:
        assert is_valid_variable_name(name) is True

    for name in ["Name", "myClass", "1a"]:
        assert is_valid_variable_name(name) is False


def test_is_valid_surfix():
    assert is_valid_surfix("大卫") is True
    

def test_to_variable_name():
    assert to_variable_name("User") == "user"
    assert to_variable_name("MyClass") == "my_class"


if __name__ == "__main__":
    test_is_valid_class_name()
    test_is_valid_variable_name()
    test_is_valid_surfix()
    test_to_variable_name()
