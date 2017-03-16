import trafaret as t

from .configus import config, maybe_get_argv, parse_envfile


def test_basic():
    env = {'var': 'hallo', 'another_var': 'holla'}
    expected = {'var': 'hallo'}
    assert config(t.Dict(var=t.String), env) == expected


def test_argv():
    assert maybe_get_argv(['--rate=1', '--backoff=2', 'debug=1']) == {'backoff': '2', 'debug': '1', 'rate': '1'}


def test_envfile():
    contents = [
    "One=one   ",
    "\texport Two=two\n\n\n \n",
    "\n\n\n \n",
    "None \n\n\n \n",
    "=",
    ]

    expected = [
        {'One': 'one'},
        {'Two': 'two'},
        {},
        {},
        {},
    ]
    for given, expected in zip(contents, expected):
        assert parse_envfile([given]) ==  expected
