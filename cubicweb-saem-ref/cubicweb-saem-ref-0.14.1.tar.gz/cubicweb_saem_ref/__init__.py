# coding: utf-8
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
"""cubicweb-saem_ref application package

Référenciel de Système d'Archivage Électronique Mutualisé
"""

from functools import partial

from six import text_type

from logilab.common.registry import objectify_predicate

from cubicweb import neg_role
from cubes.compound import CompositeGraph


# Composite graph definitions used in permissions setup.
PERMISSIONS_GRAPHS = dict.fromkeys(
    ('AuthorityRecord', 'ConceptScheme', 'SEDAArchiveTransfer'),
    partial(CompositeGraph, skiprtypes=('generated', 'used')))


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


def cwuri_url(entity):
    """Return an absolute URL for entity's cwuri, handling case where ark is directly used, and so
    URL should be generated from it.
    """
    cwuri = entity.cwuri
    if cwuri.startswith('ark:'):
        cwuri = entity._cw.build_url(cwuri)
    return cwuri


def permanent_url(entity):
    """Return permanent URL for an entity: either ark based if entity has an ark, or <site url>/<eid>.
    """
    ark = getattr(entity, 'ark', None)
    if ark is not None:
        return entity._cw.build_url('ark:/' + ark)
    return entity._cw.build_url(text_type(entity.eid))


@objectify_predicate
def user_has_authority(cls, req, **kwargs):
    """Return 1 if the user is associated to an authority."""
    return len(req.user.authority)


@objectify_predicate
def user_has_naa(cls, req, **kwargs):
    """Return 1 if the user is associated to an authority with a NAA configured."""
    return 1 if req.user.naa is not None else 0


def includeme(config):
    config.include('.pviews')


def _massive_store_factory(cnx, **kwargs):
    from cubicweb.dataimport.massive_store import MassiveObjectStore
    from .sobjects import SAEMMetadataGenerator
    return MassiveObjectStore(cnx, metagen=SAEMMetadataGenerator(cnx), **kwargs)


def _nohook_store_factory(cnx):
    from cubicweb.dataimport.stores import NoHooRQLObjectStore
    from .sobjects import SAEMMetadataGenerator
    return NoHooRQLObjectStore(cnx, metagen=SAEMMetadataGenerator(cnx))
