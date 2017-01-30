
import os, random, string

# --- TEST FIXTURES ---

def lines(text, noblanks=True, dedent=True, lstrip=False, rstrip=True, join=False):
    """
    Grab lines from a string. First and last lines are assumed to be uninteresting if blank.
    :param text:     text to be processed
    :param dedent:   a common prefix should be stripped from each line (default `True`)
    :param noblanks: allow no blank lines at all (default `True`)
    :param lstrip:   all left space be stripped from each line (default `False`);
                     dedent and lstrip are mutualy exclusive
    :param rstrip:   all right space be stripped from each line (default `True`)
    :param join:     if False, no effect; otherwise a string used to join the lines
    """

    textlines = text.expandtabs().splitlines()

    # remove blank lines if noblanks
    if noblanks:
        textlines = [ line for line in textlines if line.strip() != '' ]
    else:
        # even if intermediate blank lines ok, first and last are due to Python formatting
        if textlines and textlines[0].strip() == "":
            textlines.pop(0)
        if textlines and textlines[-1].strip() == "":
            textlines.pop()

    if dedent and not lstrip:
        nonblanklines = [ line for line in textlines if line.strip() != "" ]
        prefix = os.path.commonprefix(nonblanklines)
        prelen, maxprelen = 0, len(prefix)
        while prelen < maxprelen and prefix[prelen] == ' ':
            prelen += 1
        if prelen:
            textlines = [ line[prelen:] for line in textlines ]

    # perform requested left and right space stripping (must be done
    # late so as to not interfere with dedent's common prefix detection)
    if lstrip and rstrip:
        textlines = [ line.strip() for line in textlines ]
    elif lstrip:
        textlines = [ line.lstrip() for line in textlines ]
    elif rstrip:
        textlines = [ line.rstrip() for line in textlines ]

    if join is False:
        return textlines
    else:
        if join is True:
            join = ''
        return join.join(textlines)


def textlines(text, **kwargs):
    """
    Like ``lines()``, but returns result as unified text. Useful primarily because
    of the nice cleanups ``lines()`` does.
    """
    sep = kwargs.get('join', None)
    if sep is None or sep is False:
        kwargs['join'] = '\n'
    return lines(text, **kwargs)

ALPHABET = string.ascii_lowercase + string.digits

def tempfile(text, tmpdir):
    """
    Make a temporary file.
    :text: Text contents to add to the file.
    :name: File name. If None, chosen randomly.
    """
    name = ''.join(random.choice(ALPHABET) for i in range(12)) + '.py'
    p = tmpdir.join(name)
    p.write(textlines(text))
    return p



# --- END TEST FIXTURES ---

from show.introspect import *

CallArgs.add_target_func('show')

def test_callargs_one(tmpdir):
    p = tempfile("""
        def func():
            x = 12
            show(x)
    """, tmpdir=tmpdir)

    assert CallArgs(p.strpath, 3).args == ['x']

def test_callargs_two(tmpdir):
    p = tempfile("""
        def func():
            x = 12
            y = 99
            show(x, y)
    """, tmpdir=tmpdir)

    assert CallArgs(p.strpath, 4).args == ['x', 'y']

def test_callargs_three(tmpdir):
    p = tempfile("""
        def func():
            x = 12
            y = 99
            show(x, y, x)
    """, tmpdir=tmpdir)

    assert CallArgs(p.strpath, 4).args == ['x', 'y', 'x']

def test_callargs_four(tmpdir):
    p = tempfile("""
        def func(x, z):
            def nested(y):
                show.dir(x, y, z)
            y = 99
            show(y, x)
    """, tmpdir=tmpdir)

    assert CallArgs(p.strpath, 3).args == ['x', 'y', 'z']
    assert CallArgs(p.strpath, 5).args == ['y', 'x']


def test_ClassProps():
    c = ClassProps(dict)
    assert 'keys' in c.props
    assert c.mro == (dict, object)

    class Slotted(object):
        __slots__ = ['a', 'b']

    cs = ClassProps(Slotted)
    assert 'a' in cs.props
    assert 'b' in cs.props
    

def test_class_props():
    assert 'keys' in class_props(dict)

    class Slotted(object):
        __slots__ = ['a', 'b']

    cps = class_props(Slotted)
    assert 'a' in cps
    assert 'b' in cps
