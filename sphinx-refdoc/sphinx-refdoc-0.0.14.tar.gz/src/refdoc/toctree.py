# -*- coding: utf-8 -*-
"""
Sphinx toctree directive generator.
"""
from __future__ import absolute_import
from os.path import splitext


class Toctree(object):
    """ This class helps building Sphinx toctrees.

    :param int maxdepth:
        The number of levels included in the TOC. If the TOC entry has
        children and ``maxdepth > 1`` those children will be inlined
        as well. This makes the toctree a tree.
    """

    def __init__(self, maxdepth=1):
        self.maxdepth = maxdepth
        self.indent = 4
        self.entries = []

    def add(self, entry):
        """ Add entry to the TOC.

        :param str entry:
            This is a relative path to the ReST file. The function can
            correctly handle cases where the path is given with the ext or
            without (as Sphinx uses file names without the extension for
            toctree entries).
        """
        name, _ = splitext(entry)
        self.entries.append(name)

    def __str__(self):
        """
        :return str:
            The sphinx ``toctree`` directive.
        """
        indent = ' ' * self.indent

        toctree_directive = [
            '.. toctree::',
            indent + ':maxdepth: 1',
            '',
        ] + [
            indent + e for e in self.entries
        ] + [
            ''
        ]

        return '\n'.join(toctree_directive)
