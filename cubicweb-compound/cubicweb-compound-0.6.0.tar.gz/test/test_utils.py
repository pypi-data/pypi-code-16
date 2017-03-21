# copyright 2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-compound tests for utils module"""

from cubicweb.devtools.testlib import CubicWebTC

from cubicweb_compound import CompositeGraph
from cubicweb_compound import utils


class UtilityFunctionsTC(CubicWebTC):

    def test_graph_relations(self):
        graph = CompositeGraph(self.schema)
        structure = graph.parent_structure('Agent')
        structurals, optionals, mandatories = utils.graph_relations(
            self.schema, structure)
        expected = set([
            ('event', 'object'),
            ('biography', 'object'),
            ('relates', 'object'),
            ('account', 'object'),
            ('narrated_by', 'subject'),
            ('comments', 'subject'),
        ])
        self.assertEqual(structurals, expected)
        expected = set([
            ('narrated_by', 'subject'),
            ('relates', 'object'),
        ])
        self.assertEqual(optionals, expected)
        mandatories = [(str(rdef), role) for rdef, role in mandatories]
        expected = [
            ('account', 'object'),
            ('biography', 'object'),
            ('comments', 'subject'),
            ('event', 'object'),
        ]
        self.assertEqual(sorted(mandatories), expected)

    def test_optional_relations(self):
        graph = CompositeGraph(self.schema)
        structure = graph.parent_structure('Agent')
        optional = utils.optional_relations(self.schema, structure)
        expected = {
            'Anecdote': set([('narrated_by', 'subject')]),
            'Event': set([('relates', 'object')]),
        }
        self.assertEqual(optional, expected)

    def test_mandatory_rdefs(self):
        graph = CompositeGraph(self.schema)
        structure = graph.parent_structure('Agent')
        mandatory = [
            (str(rdef), role)
            for rdef, role in utils.mandatory_rdefs(self.schema, structure)
        ]
        expected = [
            ('relation Agent account OnlineAccount', 'subject'),
            ('relation Agent biography Biography', 'subject'),
            ('relation Biography event Anecdote', 'subject'),
            ('relation Biography event Event', 'subject'),
            ('relation Comment comments Anecdote', 'object'),
            ('relation Comment comments Comment', 'object'),
        ]
        self.assertEqual(sorted(mandatory), expected)


if __name__ == '__main__':
    import unittest
    unittest.main()
