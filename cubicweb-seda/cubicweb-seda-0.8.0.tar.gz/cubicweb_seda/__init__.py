# copyright 2016-2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-seda application package

Data Exchange Standard for Archival
"""

from cubicweb import neg_role

from cubicweb_compound import structure_def, skip_rtypes_set


def seda_profile_container_def(schema):
    """Define container for SEDAProfile"""
    return structure_def(schema, 'SEDAArchiveTransfer').items()


def iter_external_rdefs(eschema, skip_rtypes=skip_rtypes_set(['container'])):
    """Return an iterator on (rdef, role) of external relations from entity schema (i.e.
    non-composite relations).
    """
    for rschema, targets, role in eschema.relation_definitions():
        if rschema in skip_rtypes:
            continue
        for target_etype in targets:
            rdef = eschema.rdef(rschema, role, target_etype)
            if rdef.composite:
                continue
            yield rdef, role


def iter_all_rdefs(schema, container_etype):
    """Return an iterator on (rdef, role) of all relations of the compound graph starting from the
    given entity type, both internal (composite) and external (non-composite).
    """
    for etype, parent_rdefs in structure_def(schema, container_etype).items():
        for rtype, role in parent_rdefs:
            for rdef in schema[rtype].rdefs.values():
                yield rdef, neg_role(role)
        for rdef, role in iter_external_rdefs(schema[etype]):
                yield rdef, role
    for rdef, role in iter_external_rdefs(schema[container_etype]):
        yield rdef, role
