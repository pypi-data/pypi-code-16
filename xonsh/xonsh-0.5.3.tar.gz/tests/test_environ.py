# -*- coding: utf-8 -*-
"""Tests the xonsh environment."""
from __future__ import unicode_literals, print_function
import os
import tempfile
import builtins
from tempfile import TemporaryDirectory
from xonsh.tools import ON_WINDOWS

import pytest

from xonsh.commands_cache import CommandsCache
from xonsh.environ import Env, load_static_config, locate_binary

from tools import skip_if_on_unix

def test_env_normal():
    env = Env(VAR='wakka')
    assert 'wakka' == env['VAR']

def test_env_contains():
    env = Env(VAR='wakka')
    assert 'VAR' in env

@pytest.mark.parametrize('path', [['/home/wakka'], ['wakka']])
def test_env_path_list(path):
    env = Env(MYPATH=path)
    assert path == env['MYPATH'].paths

@pytest.mark.parametrize('path', [
    ['/home/wakka' + os.pathsep + '/home/jawaka'],
    ['wakka' + os.pathsep + 'jawaka']
])
def test_env_path_str(path):
    env = Env(MYPATH=path)
    assert path == env['MYPATH'].paths

def test_env_detype():
    env = Env(MYPATH=['wakka', 'jawaka'])
    assert 'wakka' + os.pathsep + 'jawaka' == env.detype()['MYPATH']

@pytest.mark.parametrize('path1, path2',[
    (['/home/wakka', '/home/jawaka'], '/home/woah'),
    (['wakka', 'jawaka'], 'woah')
])
def test_env_detype_mutable_access_clear(path1, path2):
    env = Env(MYPATH=path1)
    assert path1[0] + os.pathsep + path1[1] == env.detype()['MYPATH']
    env['MYPATH'][0] = path2
    assert env._detyped is None
    assert path2 + os.pathsep + path1[1] == env.detype()['MYPATH']

def test_env_detype_no_dict():
    env = Env(YO={'hey': 42})
    det = env.detype()
    assert 'YO' not in det

def test_histcontrol_none():
    env = Env(HISTCONTROL=None)
    assert isinstance(env['HISTCONTROL'], set)
    assert len(env['HISTCONTROL']) == 0

def test_HISTCONTROL_empty():
    env = Env(HISTCONTROL='')
    assert isinstance(env['HISTCONTROL'], set)
    assert len(env['HISTCONTROL']) == 0

def test_histcontrol_ignoredups():
    env = Env(HISTCONTROL='ignoredups')
    assert isinstance(env['HISTCONTROL'], set)
    assert len(env['HISTCONTROL']) == 1
    assert ('ignoredups' in env['HISTCONTROL'])
    assert ('ignoreerr' not in env['HISTCONTROL'])

def test_histcontrol_ignoreerr_ignoredups():
    env = Env(HISTCONTROL='ignoreerr,ignoredups,ignoreerr')
    assert len(env['HISTCONTROL']) == 2
    assert ('ignoreerr' in env['HISTCONTROL'])
    assert ('ignoredups' in env['HISTCONTROL'])

def test_swap():
    env = Env(VAR='wakka')
    assert env['VAR'] == 'wakka'

    # positional arg
    with env.swap({'VAR': 'foo'}):
        assert env['VAR'] == 'foo'

    # make sure the environment goes back outside the context manager
    assert env['VAR'] == 'wakka'

    # kwargs only
    with env.swap(VAR1='foo', VAR2='bar'):
        assert env['VAR1'] == 'foo'
        assert env['VAR2'] == 'bar'

    # positional and kwargs
    with env.swap({'VAR3': 'baz'}, VAR1='foo', VAR2='bar'):
        assert env['VAR1'] == 'foo'
        assert env['VAR2'] == 'bar'
        assert env['VAR3'] == 'baz'

    # make sure the environment goes back outside the context manager
    assert env['VAR'] == 'wakka'
    assert 'VAR1' not in env
    assert 'VAR2' not in env
    assert 'VAR3' not in env


@pytest.mark.parametrize('s, exp, loaded',[
    (b'{"best": "awash"}', {'best': 'awash'}, True), # works
    (b'["best", "awash"]', {}, False), # fail
    (b'{"best": "awash"', {}, False) # json fail
])
def test_load_static_config(s, exp, loaded, tmpdir, xonsh_builtins):
    env = Env({'XONSH_SHOW_TRACEBACK': False})
    xonsh_builtins.__xonsh_env__ = env
    f = tmpdir.join('test_static_config')
    f.write(s)
    conf = load_static_config(env, str(f))
    assert exp == conf
    assert env['LOADED_CONFIG'] == loaded


@skip_if_on_unix
def test_locate_binary_on_windows(xonsh_builtins):
    files = ('file1.exe', 'FILE2.BAT', 'file3.txt')
    with TemporaryDirectory() as tmpdir:
        for fname in files:
            fpath = os.path.join(tmpdir, fname)
            with open(fpath, 'w') as f:
                f.write(fpath)
        xonsh_builtins.__xonsh_env__.update({
            'PATH': [tmpdir],
            'PATHEXT': ['.COM', '.EXE', '.BAT'],
        })
        xonsh_builtins.__xonsh_commands_cache__ = CommandsCache()
        assert locate_binary('file1') == os.path.join(tmpdir, 'file1.exe')
        assert locate_binary('file1.exe') == os.path.join(tmpdir, 'file1.exe')
        assert locate_binary('file2') == os.path.join(tmpdir, 'FILE2.BAT')
        assert locate_binary('file2.bat') == os.path.join(tmpdir, 'FILE2.BAT')
        assert locate_binary('file3') is None
