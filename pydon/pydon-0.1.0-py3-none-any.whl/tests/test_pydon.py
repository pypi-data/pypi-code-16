import re

from pydon import (
    load_string,
    load_file,
    dump_string,
    dump_file,
)


def strip_whitespace(text):
    return re.sub(r'\s+', '', text)


def test_load_string():
    text = "{'a': 1, 'b': '2', 'c': [3, 4, 5]}"
    data = load_string(text)
    assert data == {'a': 1, 'b': '2', 'c': [3, 4, 5]}


def test_load_file(find_data_file):
    data = load_file(find_data_file('simple.pydon'))
    assert data == {'a': 1, 'b': '2', 'c': [3, 4, 5]}


def test_dump_string():
    data = {'a': 1, 'b': '2', 'c': [3, 4, 5]}
    computed_text = strip_whitespace(dump_string(data))
    expected_text = strip_whitespace("{'a': 1, 'b': '2', 'c': [3, 4, 5]}")
    assert computed_text == expected_text


def test_dump_file(tmpdir):
    filename = tmpdir.join('test.pydon')
    data = {'a': 1, 'b': '2', 'c': [3, 4, 5]}
    dump_file(data, str(filename))
    with open(str(filename)) as test_file:
        text = test_file.read()
    computed_text = strip_whitespace(text)
    expected_text = strip_whitespace("{'a': 1, 'b': '2', 'c': [3, 4, 5]}")
    assert computed_text == expected_text
