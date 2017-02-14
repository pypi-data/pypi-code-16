import os
import unittest
import doctest
import subprocess


here = os.path.dirname(__file__)
buildout_directory = os.path.dirname(
        os.path.dirname(
            os.path.dirname(here)))


def project_path(*parts):
    return os.path.join(buildout_directory, *parts)


def _run(script, *args):
    cmd = (project_path(script),) + args
    return subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)


def run(script, *args):
    p = _run(script, *args)
    stdout, stderr = p.communicate()
    if p.returncode > 0:
        return stdout, stderr
        raise RuntimeError("Command Failed %s", p.returncode)
    return stdout, stderr


def setUp(test):
    test.globs['run'] = run


def tearDown(test):
    pass


def create_suite(testfile,
                 layer=None,
                 level=None,
                 setUp=setUp,
                 tearDown=tearDown,
                 cls=doctest.DocFileSuite,
                 encoding='utf-8'):
    suite = cls(
        testfile, tearDown=tearDown, setUp=setUp,
        optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
        encoding=encoding)
    if layer:
        suite.layer = layer
    if level:
        suite.level = level
    return suite


def test_suite():
    return unittest.TestSuite((
        create_suite('render.rst'),
        create_suite('usage.rst'),
    ))
