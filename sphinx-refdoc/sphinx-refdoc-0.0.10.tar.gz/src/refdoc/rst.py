# -*- coding: utf-8 -*-
from __future__ import absolute_import


def title(title):
    """ Generate reST title directive.

    :Examples:

    >>> section('Page title')
    '''
    ==========
    Page title
    ==========
    <BLANKLINE>
    '''

    """
    title_len  = len(title)
    return '\n'.join((
        '',
        '=' * title_len,
        title,
        '=' * title_len,
        '',
    ))


def section(name, underline_char='='):
    """ Generate reST section directive with the given underline.

    :Examples:

    >>> section('My section')
    '''
    My section
    ==========
    <BLANKLINE>
    '''

    >>> section('Subsection', '~')
    '''
    Subsection
    ~~~~~~~~~~
    <BLANKLINE>
    '''

    """
    name_len  = len(name)
    return '\n'.join((
        '',
        name,
        underline_char * name_len,
        '',
    ))


def automodule(name):
    """ Generate reST automodule directive for the given module.

    :Examples:

    >>> automodule('my.test.module')
    '''
    .. automodule:: my.test.module
        :members:
    <BLANKLINE>
    '''
    """
    return '\n'.join((
        '',
        '.. automodule:: {}'.format(name),
        '    :members:',
        '',
    ))
