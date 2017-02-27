# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:expandtab

# Copyright 2016 juxor <ju@riseup.net>

# This file is part of afaq-dl.
#
# afaqdl is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# afaqdl is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with afaqdl.  If not, see <http://www.gnu.org/licenses/>.
""""""

try:
    from ._version import version
except ImportError:
    try:
        from setuptools_scm import get_version
        version = get_version()
    except (ImportError, LookupError):
        version = '0.7'

__version__ = version
__author__ = "juxor"
__author_mail__ = "ju@riseup.net"
__description__ = "Download the online book An Anarchist FAQ"
__long_description__ = """Download the online book An Anarchist FAQ (AFAQ)
convert the HTML to Markdown and push the changes to the afaq repository."""
__website__ = 'https://github.com/juxor/afaq-dl'
__documentation__ = 'http://afaqdl.readthedocs.io/en/' + __version__
__authors__ = []
__copyright__ = """Copyright (C) 2016 <ju@riseup.net>
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
For details see the COPYRIGHT file distributed along this program."""

__license__ = """
    This package is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    any later version.

    This package is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this package. If not, see <http://www.gnu.org/licenses/>.
"""
__all__ = ['utils', 'spiders']