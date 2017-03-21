# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""Library functions to ease usual tasks one wants to achieve using compound
based entities graph:

* traversing the graph (:func:`optional_relations`,
  :func:`optional_mandatory_rdefs`, :func:`graph_relations`),

* setting permisssions (:func:`graph_set_etypes_update_permissions`,
  :func:`graph_set_write_rdefs_permissions`).
"""

from six.moves import reduce

from cubicweb import neg_role
from cubicweb.schema import ERQLExpression, RRQLExpression


def graph_relations(schema, parent_structure):
    """Given a parent structure of a composite graph (and a schema object),
    return relation information `(rtype, role)` sets where `role` is the role
    of the child in the relation for the following kinds of relations:

    * structural relations,
    * optional relations (cardinality of the child not in '1*'),
    * mandatory relations (cardinality of the child in '1*').
    """
    def concat_sets(sets):
        """Concatenate sets"""
        return reduce(lambda x, y: x | y, sets, set())

    optionals = concat_sets(
        optional_relations(schema, parent_structure).values())
    mandatories = set([
        (rdef.rtype, neg_role(role))
        for rdef, role in mandatory_rdefs(schema, parent_structure)])
    structurals = concat_sets(map(set, parent_structure.values()))
    return structurals, optionals, mandatories


def optional_relations(schema, graph_structure):
    """Return a dict with optional relations information in a CompositeGraph.

    Keys are names of entity types in the graph for which a relation type has
    no mandatory (cardinality in '1+') relation definitions and values is a
    set of respective `(rtype, role)` tuples.
    """
    optionals = dict()
    for etype, relations in graph_structure.iteritems():
        for (rtype, role), targets in relations.iteritems():
            for target in targets:
                rdef = schema[rtype].role_rdef(etype, target, role)
                if rdef.role_cardinality(role) in '1+':
                    break
            else:
                optionals.setdefault(etype, set()).add((rtype, role))
    return optionals


def mandatory_rdefs(schema, graph_structure):
    """Yield non-optional relation definitions (and the role of the parent in
    the relation) in a graph structure.
    """
    visited = set()
    for etype, relations in graph_structure.iteritems():
        for (rtype, role), targets in relations.iteritems():
            for target in targets:
                rdef = schema[rtype].role_rdef(etype, target, role)
                if rdef in visited:
                    continue
                visited.add(rdef)
                if rdef.role_cardinality(role) in '1+':
                    yield rdef, neg_role(role)


def graph_set_etypes_update_permissions(schema, graph, etype):
    """Add `action` permissions for all entity types in the composite `graph`
    with root `etype`. Respective permissions that are inserted on each
    entity type are relative to the "parent" in the relation from this
    entity type walking up to the graph root.

    So for instance, calling `set_etype_permissions('R', 'update')`
    on a schema where `A related_to B` and `R root_of B` one will get:

    * "U has_update_permission R, R root_of X" for `B` entity type and,
    * "U has_update_permission P, X related_to P" for `A` entity type.

    If an entity type in the graph is reachable through multiple relations, a
    permission for each of this relation will be inserted so that if any of
    these match, the permission check will succeed.
    """
    structure = graph.parent_structure(etype)
    optionals = optional_relations(schema, structure)
    for child, relations in structure.iteritems():
        skiprels = optionals.get(child, set())
        exprs = []
        for rtype, role in relations:
            if (rtype, role) in skiprels:
                continue
            relexpr = _rel_expr(rtype, role)
            exprs.append('{relexpr}, U has_update_permission A'.format(relexpr=relexpr))
        if exprs:
            for action in ('update', 'delete'):
                schema[child].set_action_permissions(action,
                                                     tuple(ERQLExpression(e) for e in exprs))


def graph_set_write_rdefs_permissions(schema, graph, etype):
    """Set 'add' and 'delete' permissions for all mandatory relation
    definitions in the composite `graph` with root `etype`.

    Respective permissions that are inserted on each relation definition are
    relative to the "parent" in the relation from this entity type walking up
    to the graph root.

    Relations which are not mandatory or which are not part of the graph
    structure should be handled manually.
    """
    structure = graph.parent_structure(etype)
    for rdef, parent_role in mandatory_rdefs(schema, structure):
        var = {'object': 'O', 'subject': 'S'}[parent_role]
        expr = 'U has_update_permission {0}'.format(var)
        for action in ('add', 'delete'):
            rdef.set_action_permissions(action, (RRQLExpression(expr), ))


def _rel_expr(rtype, role):
    return {'subject': 'X {rtype} A',
            'object': 'A {rtype} X'}[role].format(rtype=rtype)
