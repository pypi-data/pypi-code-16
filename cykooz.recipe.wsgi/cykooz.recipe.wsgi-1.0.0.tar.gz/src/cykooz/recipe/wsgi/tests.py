# cykooz.recipe.wsgi
# Copyright (C) 2017 Cykooz
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
from __future__ import print_function
import doctest
import unittest

from zc.buildout import testing


def buildoutSetUp(test):
    testing.buildoutSetUp(test)
    testing.install_develop('cykooz.recipe.wsgi', test)
    test.globs['print'] = print


class RecipeUnitTest(unittest.TestCase):

    def __new__(cls, test):
        return getattr(cls, test)()

    @classmethod
    def test_recipe(cls):
        return doctest.DocFileSuite('recipe.txt',
                                    setUp=buildoutSetUp, tearDown=testing.buildoutTearDown,
                                    optionflags=(doctest.ELLIPSIS | doctest.REPORT_ONLY_FIRST_FAILURE))
