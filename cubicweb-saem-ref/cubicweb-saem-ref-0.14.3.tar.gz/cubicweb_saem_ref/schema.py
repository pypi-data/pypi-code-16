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
"""cubicweb-saem-ref schema"""

from yams.buildobjs import EntityType, RelationDefinition, String, Int, ComputedRelation
from yams.constraints import UniqueConstraint

from cubicweb import _
from cubicweb.schema import (RO_ATTR_PERMS, ERQLExpression, RRQLExpression,
                             RQLConstraint, RQLVocabularyConstraint, WorkflowableEntityType,
                             make_workflowable)
from cubicweb.schemas.base import ExternalUri, EmailAddress

from cubes.skos.schema import ConceptScheme
from cubes.eac.schema import AuthorityRecord, NameEntry
from cubes.seda.schema import simplified_profile
from cubes.seda.schema.seda2 import SEDAArchiveTransfer

from . import PERMISSIONS_GRAPHS, optional_relations, mandatory_rdefs


def publication_permissions(cls):
    """Set __permissions__ of `cls` entity type class preventing modification
    when not in state "draft".
    """
    cls.__permissions__ = cls.__permissions__.copy()
    cls.__permissions__['update'] = (
        ERQLExpression('U in_group G, G name IN ("managers", "users"), '
                       'X in_state ST, ST name "draft"'),
    )
    cls.__permissions__['delete'] = (
        ERQLExpression('U in_group G, G name IN ("managers", "users"), '
                       'X in_state ST, ST name "draft"'),
    )
    return cls


def groups_permissions(cls):
    """Set __permissions__ of `cls` entity type class preventing modification
    when user is not in managers or users group.
    """
    cls.__permissions__ = cls.__permissions__.copy()
    cls.__permissions__['update'] = (
        ERQLExpression('U in_group G, G name IN ("managers", "users")', 'U'),
    )
    return cls


def _rel_expr(rtype, role):
    return {'subject': 'X {rtype} A',
            'object': 'A {rtype} X'}[role].format(rtype=rtype)


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
    """Set 'add' and 'delete' permissions for all mandatory relation definitions in the composite
    `graph` with root `etype`.

    Respective permissions that are inserted on each relation definition are relative to the
    "parent" in the relation from this entity type walking up to the graph root.

    Relations which are not mandatory or which are not part of the graph structure should be handled
    manually.
    """
    structure = graph.parent_structure(etype)
    for rdef, parent_role in mandatory_rdefs(schema, structure):
        var = {'object': 'O', 'subject': 'S'}[parent_role]
        expr = 'U has_update_permission {0}'.format(var)
        for action in ('add', 'delete'):
            rdef.set_action_permissions(action, (RRQLExpression(expr), ))


# Disable "update" for ExternalUri as these should only come from imported data
# and are meant to only be created or deleted.
ExternalUri.__permissions__ = ExternalUri.__permissions__.copy()
ExternalUri.__permissions__['update'] = ()


# Customization of EmailAddress entity type.
EmailAddress.remove_relation('alias')


# Customization of eac schema.
make_workflowable(AuthorityRecord)
groups_permissions(AuthorityRecord)
# XXX can be removed once we depend on eac > 0.3
NameEntry.get_relation('form_variant').internationalizable = True


# Customization of skos schema.
make_workflowable(ConceptScheme)
publication_permissions(ConceptScheme)


class Organization(EntityType):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', ),
        'update': ('managers', ),
        'delete': ('managers', ),
    }
    name = String(required=True, fulltextindexed=True, unique=True)


class OrganizationUnit(WorkflowableEntityType):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', ),
        'update': ('managers', ),
        'delete': ('managers', ),
    }
    __unique_together__ = [('name', 'authority')]
    name = String(required=True, fulltextindexed=True, unique=True)


@groups_permissions
class Agent(WorkflowableEntityType):
    name = String(required=True, fulltextindexed=True)


class user_authority(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers',),
        'delete': (),
    }
    name = 'authority'
    subject = 'CWUser'
    object = 'Organization'
    cardinality = '?*'
    inlined = True
    constraints = [
        RQLConstraint('NOT EXISTS(A agent_user S) '
                      'OR EXISTS(B agent_user S, B authority O)'),
    ]


class others_authority(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', RRQLExpression('U authority O'),),
        'delete': (),
    }
    name = 'authority'
    subject = ('OrganizationUnit', 'Agent')
    object = 'Organization'
    cardinality = '1*'
    composite = 'object'
    inlined = True


class agent_user(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers',),
        'delete': ('managers',),
    }
    subject = 'Agent'
    object = 'CWUser'
    cardinality = '??'
    inlined = True
    description = _('the application user related to this agent')
    constraints = [
        RQLConstraint('NOT EXISTS(O authority A) '
                      'OR EXISTS(O authority B, S authority B)'),
    ]


class associated_with(RelationDefinition):
    subject = 'Activity'
    object = 'CWUser'


class _authority_record(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers',),
        'delete': ('managers',),
    }
    name = 'authority_record'
    object = 'AuthorityRecord'
    cardinality = '??'
    inlined = True
    description = _('the authority record describing this agent')


class ou_authority_record(_authority_record):
    subject = 'OrganizationUnit'
    description = _('the authority record describing this organization unit')
    constraints = [
        RQLConstraint('O agent_kind K, K name "authority"'),
    ]


class o_authority_record(ou_authority_record):
    subject = 'Organization'
    description = _('the authority record describing this organization')


class agent_authority_record(_authority_record):
    subject = 'Agent'
    description = _('the authority record describing this agent')
    constraints = [
        RQLConstraint('O agent_kind K, K name "person"'),
    ]


class contact_point(RelationDefinition):
    subject = 'OrganizationUnit'
    object = 'Agent'
    cardinality = '?*'
    inlined = True
    constraints = [
        RQLConstraint('S authority A, O authority A'),
        RQLVocabularyConstraint('O in_state ST, ST name "published"'),
    ]
    description = _('set an agent as the contact point of an organization unit')


class archival_unit(RelationDefinition):
    subject = 'Organization'
    object = 'OrganizationUnit'
    cardinality = '?*'
    description = _("the archival unit responsible for dealing with the organization's "
                    "documents")
    constraints = [RQLConstraint('O archival_role AR, AR name "archival"'),
                   RQLVocabularyConstraint('O in_state ST, ST name "published"')]


class archival_authority(ComputedRelation):
    rule = 'S archival_unit OU, OU authority O'


class use_authorityrecord(RelationDefinition):
    subject = 'OrganizationUnit'
    object = 'AuthorityRecord'
    cardinality = '**'
    description = _("authority records used by this archival unit")
    constraints = [
        RQLConstraint('S archival_role AR, AR name "archival"'),
    ]


class ArchivalRole(EntityType):
    """An archival role determines the kind of action (e.g. deposit or control)
    an agent may perform on an archive entity.
    """
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', ),
        'update': ('managers', ),
        'delete': ('managers', ),
    }
    name = String(required=True, unique=True, internationalizable=True)


class archival_role(RelationDefinition):
    subject = 'OrganizationUnit'
    object = 'ArchivalRole'
    cardinality = '**'
    description = _("the organization unit's archival role (producer, control, etc.)")


class use_email(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests',),
        'add': ('managers', RRQLExpression('U has_update_permission S'),),
        'delete': ('managers', RRQLExpression('U has_update_permission S'),),
    }
    subject = 'Agent'
    object = 'EmailAddress'
    cardinality = '*?'
    composite = 'subject'
    fulltext_container = 'subject'


class phone_number(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests',),
        'add': ('managers', RRQLExpression('U has_update_permission S'),),
        'delete': ('managers', RRQLExpression('U has_update_permission S'),),
    }
    subject = 'Agent'
    object = 'PhoneNumber'
    cardinality = '*1'
    composite = 'subject'


class related_concept_scheme(RelationDefinition):
    subject = 'OrganizationUnit'
    object = 'ConceptScheme'
    cardinality = '**'
    description = _('concept schemes used by the agent')


class generated(RelationDefinition):
    subject = 'Activity'
    object = ('Concept', 'ConceptScheme')


class used(RelationDefinition):
    subject = 'Activity'
    object = ('Concept', 'ConceptScheme')


# ARK ##########################################################################

class ark(RelationDefinition):
    __permissions__ = RO_ATTR_PERMS
    subject = (
        'Agent',
        'AuthorityRecord',
        'Concept',
        'ConceptScheme',
        'Organization',
        'OrganizationUnit',
        'SEDAArchiveTransfer',
    )
    object = 'String'
    description = _('ARK Identifier - will be generated if not specified')
    constraints = [UniqueConstraint()]
    cardinality = '11'


class ArkNameAssigningAuthority(EntityType):
    """Name Assigning Authority (NAA) for ARK generation."""
    who = String(required=True, unique=True,
                 description=_('official organization name'))
    what = Int(required=True, unique=True,
               description=_('Name Assigning Authority Number (NAAN)'))


class _ark_naa(RelationDefinition):
    name = 'ark_naa'
    object = 'ArkNameAssigningAuthority'
    inlined = True


class organization_ark_naa(_ark_naa):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', ),
        'delete': ('managers', ),
    }
    subject = 'Organization'
    cardinality = '?*'
    description = _("ARK identifier Name Assigning Authority (NAA) - "
                    "you'll need one to start creating objects")


class mandatory_ark_naa(_ark_naa):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', 'users',),
        'delete': (),
    }
    subject = ('AuthorityRecord', 'SEDAArchiveTransfer')
    cardinality = '1*'
    description = _("ARK identifier Name Assigning Authority (NAA)")


class optional_ark_naa(_ark_naa):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', 'users',),
        'delete': (),
    }
    subject = ('ConceptScheme', 'SKOSSource')
    cardinality = '?*'
    description = _("ARK identifier Name Assigning Authority (NAA), "
                    "necessary to create ARK for concepts which don't have one yet.")


# SEDA #######################################################################

make_workflowable(SEDAArchiveTransfer)
publication_permissions(SEDAArchiveTransfer)


simplified_profile.default = True


class use_profile(RelationDefinition):
    subject = 'OrganizationUnit'
    object = 'SEDAArchiveTransfer'
    cardinality = '**'
    constraints = [RQLConstraint('S archival_role R, R name "deposit"')]


class new_version_of(RelationDefinition):
    __permissions__ = {'read': ('managers', 'users', 'guests'),
                       'add': ('managers', 'users',
                               RRQLExpression('O in_state ST, ST name "published"')),
                       'delete': ()}
    subject = 'SEDAArchiveTransfer'
    object = 'SEDAArchiveTransfer'
    cardinality = '??'
    inlined = True


def post_build_callback(schema):
    schema['simplified_profile'].rdefs['SEDAArchiveTransfer', 'Boolean'].default = True  # XXX
    for etype, graph in PERMISSIONS_GRAPHS.iteritems():
        if etype == 'SEDAArchiveTransfer':
            # this compound graph as a generic 'container' relation on which security is based
            continue
        graph_set_etypes_update_permissions(schema, graph(schema), etype)
        graph_set_write_rdefs_permissions(schema, graph(schema), etype)

    # permissions override
    schema['Label'].set_action_permissions('delete', ('managers', 'users'))
    for rtype in ('in_scheme', 'broader_concept', 'label_of'):
        for rdef in schema[rtype].rdefs.values():
            rdef.set_action_permissions('add', ('managers', 'users'))
            if rtype == 'label_of':
                rdef.set_action_permissions('delete', ('managers', 'users'))
