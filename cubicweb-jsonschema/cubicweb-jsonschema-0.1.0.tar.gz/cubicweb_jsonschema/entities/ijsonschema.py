# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-jsonschema entity's classes"""

from collections import OrderedDict
from itertools import chain

from six import text_type

import jsl
import jsonschema

from logilab.common.registry import objectify_predicate

from cubicweb import ValidationError, neg_role
from cubicweb.predicates import match_kwargs, non_final_entity
from cubicweb.schema import VIRTUAL_RTYPES
from cubicweb.view import Adapter, EntityAdapter

from cubicweb_jsonschema import VIEW_ROLE, CREATION_ROLE, EDITION_ROLE
from . import orm_rtype


def editable_fields(cnx, action, entity):
    """Yield (rtype, role, target_types) for editable fields for `action` and
    possibly existing `entity`. Fields are attributes and relations defined in
    the "inlined" of uicfg.autoform_section.
    """
    uicfg_afs = cnx.vreg['uicfg'].select(
        'autoform_section', cnx, entity=entity)
    relations_action = 'add' if action == 'update' else action
    schema_fields = chain(
        uicfg_afs.relations_by_section(
            entity, 'main', 'attributes', action),
        uicfg_afs.relations_by_section(
            entity, 'main', 'inlined', relations_action),
    )
    for rschema, tschemas, role in schema_fields:
        yield rschema.type, role, set(t.type for t in tschemas)


def visible_fields(cnx, entity=None, etype=None):
    """Yield (rtype, role, target_types) for visible fields of `entity`.
    Fields are attributes and relations visible as per
    uicfg.primaryview_section.
    """
    # Adapted from cubicweb.web.views.primary:PrimaryView._section_def
    rsection = cnx.vreg['uicfg'].select(
        'primaryview_section', cnx, entity=entity)
    if entity is not None:
        eschema = entity.e_schema
    elif etype is not None:
        eschema = cnx.vreg.schema[etype]
    else:
        raise ValueError('either "entity" or "etype" must be specified')
    for rschema, tschemas, role in eschema.relation_definitions(True):
        if rschema in VIRTUAL_RTYPES:
            continue
        rtype = rschema.type
        target_types = set()
        for tschema in tschemas:
            section = rsection.etype_get(eschema, rschema, role, tschema)
            if section in ('attributes', 'relations'):
                target_types.add(tschema.type)
        if target_types:
            yield rtype, role, target_types


def jsonschema_validate(schema, instance, _entity=None):
    """Validate an instance under the JSON schema."""
    try:
        jsonschema.validate(instance, schema)
    except jsonschema.ValidationError as exc:
        raise ValidationError(_entity, {None: exc.message})


def mapper_for_relation(req, etype, rtype, role, target_types=None):
    """Return a relation mapper object, responsible to map the relation definition(s) defined by
    `etype`, `rtype`, `role` and optionally `target_types`.
    """
    return req.vreg['components'].select(
        'jsonschema.map.relation', req,
        etype=etype, rtype=rtype, role=role, target_types=target_types)


def _filter_relinfo(relinfos, relinfo_to_skip):
    for rtype, role, tetypes in relinfos:
        if (rtype, role) == relinfo_to_skip:
            continue
        yield rtype, role, tetypes


def build_document_tree(cnx, etype, relinfo, schema_role):
    """Build the complete tree of JSON schema definitions needed by `etype`
    and return a jsl.DocumentField wrapping `etype` definition.
    """
    mapper = cnx.vreg['components'].select(
        'jsonschema.map.etype', cnx, etype=etype)
    maindoc, relation_targets = mapper.jsl_document(relinfo, schema_role)
    # Process references to targets of relation and build respective
    # documents.
    if schema_role == EDITION_ROLE:
        schema_role = CREATION_ROLE
    for (rtype, role), targettypes in relation_targets.items():
        reverse_relinfo = rtype, neg_role(role)
        for tetype in targettypes:
            adapted = cnx.vreg['adapters'].select(
                'IJSONSchema', cnx, etype=tetype)
            # Filter "reverse" relation definition from target entity type
            # relation information set.
            relinfo = _filter_relinfo(
                adapted.relinfo_for(schema_role), reverse_relinfo)
            # Just build the document tree for target type, triggering JSL
            # registration and hence inclusing of related document in the file
            # schema.
            build_document_tree(cnx, tetype, relinfo, schema_role)
    return jsl.fields.DocumentField(maindoc, as_ref=True)


def resource_identifier_schema():
    """Return schema for a resource identifier, inspired from
    http://jsonapi.org/format/#document-resource-identifier-objects.
    """
    # TODO: set id as readOnly
    # (http://json-schema.org/latest/json-schema-hypermedia.html#rfc.section.4.4)
    return jsl.fields.DictField(
        properties={
            'id': jsl.fields.StringField(),
            'url': jsl.fields.StringField(format='uri'),
            'title': jsl.fields.StringField(),
        }
    )


def resource_identifier(entity):
    """Return a dictionary with entity represented as a "resource identifier".
    """
    return {
        'id': text_type(entity.eid),
        'url': entity.absolute_url(),
        'title': entity.dc_title(),
    }


def collection_schema(name, title, **kwargs):
    """Return a JSON schema dict to model a collection of entities."""
    item_schema = resource_identifier_schema()
    array = jsl.fields.ArrayField(title=title, items=item_schema)
    schema_cls = OrderedDict if kwargs.get('ordered', False) else dict
    ref = jsl.fields.RefField('#/definitions/{0}'.format(name))
    schema = schema_cls({
        'definitions': {
            name: array.get_schema(**kwargs),
        },
    })
    schema.update(ref.get_schema(**kwargs))
    return schema


class IJSONSchemaMixIn(object):

    def iter_relation_mappers(self, schema_role, relinfo=None):
        """Return an iterator on `(adapter, mapper)` where adapter represent an
        entity type reachable in the context in `schema_role` (self included)
        and mapper a relation for this entity type.
        """
        relation_targets = []
        if relinfo is None:
            relinfo = self.relinfo_for(schema_role)
        etype = self.etype
        for rtype, role, target_types in relinfo:
            relation_mapper = mapper_for_relation(self._cw, etype, rtype, role, target_types)
            yield self, relation_mapper
            if relation_mapper.target_types:
                relation_targets.append((relation_mapper))
        if schema_role == EDITION_ROLE:
            schema_role = CREATION_ROLE  # XXX
        for relation_mapper in relation_targets:
            reverse_relinfo = relation_mapper.rtype, neg_role(relation_mapper.role)
            for tetype in relation_mapper.target_types:
                adapted = self._cw.vreg['adapters'].select(
                    'IJSONSchema', self._cw, etype=tetype)
                # Filter "reverse" relation definition from target entity type
                # relation information set.
                relinfo = _filter_relinfo(
                    adapted.relinfo_for(schema_role), reverse_relinfo)
                for adapter, relation_mapper in adapted.iter_relation_mappers(schema_role, relinfo):
                    yield adapter, relation_mapper


class IJSONSchemaETypeAdapter(IJSONSchemaMixIn, Adapter):
    """IJSONSchema adapter for entity creation with `etype` specified in
    selection context.

    Subclasses may refine the selection context using ``match_kwargs``
    predicates (e.g. ``match_kwargs({'etype': 'MyEtype'})`` to override JSON
    Schema generation for a particular etype).
    """
    __regid__ = 'IJSONSchema'
    __select__ = match_kwargs('etype')

    @property
    def etype(self):
        """The entity type bound to this adapter."""
        return str(self.cw_extra_kwargs['etype'])

    def view_schema(self, **kwargs):
        """Return a JSON schema suitable for viewing adapted entity."""
        relinfo = self.relinfo_for(VIEW_ROLE)
        jsldoc = build_document_tree(self._cw, self.etype, relinfo, VIEW_ROLE)
        return jsldoc.get_schema(**kwargs)

    def creation_schema(self, **kwargs):
        """Return a JSON schema suitable for entity creation."""
        etype = self.etype
        relinfo = self.relinfo_for(CREATION_ROLE)
        jsldoc = build_document_tree(self._cw, etype, relinfo, CREATION_ROLE)
        return jsldoc.get_schema(**kwargs)

    def relinfo_for(self, schema_role):
        """Return a generator of relation information tuple (rtype, role,
        targettypes) for given schema role.
        """
        etype = self.etype
        if schema_role == VIEW_ROLE:
            return visible_fields(self._cw, etype=etype)
        elif schema_role == CREATION_ROLE:
            entity = self._cw.vreg['etypes'].etype_class(etype)(self._cw)
            return editable_fields(self._cw, 'add', entity)
        else:
            raise ValueError('unhandled schema role "{0}" in {1}'.format(
                schema_role, self))

    def create_entity(self, instance):
        """Return a CubicWeb entity built from `instance` data matching this
        JSON schema.
        """
        jsonschema_validate(self.creation_schema(), instance)
        values = {}
        for adapter, relation_mapper in self.iter_relation_mappers(CREATION_ROLE):
            values.update(relation_mapper.values(None, instance))
        return self._cw.create_entity(self.etype, **values)


class IJSONSchemaRelationTargetETypeAdapter(IJSONSchemaETypeAdapter):
    """IJSONSchema adapter for entity creation of an entity of `etype` related
    through `rtype` and `role` specified in selection context.
    """
    __select__ = match_kwargs('etype', 'rtype', 'role')

    @property
    def rtype(self):
        return self.cw_extra_kwargs['rtype']

    @property
    def role(self):
        return self.cw_extra_kwargs['role']

    def relinfo_for(self, schema_role):
        """Return a generator of relation information tuple (rtype, role,
        targettypes) for given schema role.
        """
        if schema_role == CREATION_ROLE:
            entity = self._cw.vreg['etypes'].etype_class(self.etype)(self._cw)
            return _filter_relinfo(
                editable_fields(self._cw, 'add', entity), (self.rtype, self.role))
        return super(IJSONSchemaRelationTargetETypeAdapter, self).relinfo_for(schema_role)

    def create_entity(self, instance, target):
        """Return a CubicWeb entity related to `target` through relation
        information from selection context.
        """
        entity = super(IJSONSchemaRelationTargetETypeAdapter, self).create_entity(instance)
        entity.cw_set(**{orm_rtype(self.rtype, self.role): target})
        return entity


class IJSONSchemaEntityAdapter(IJSONSchemaMixIn, EntityAdapter):
    """IJSONSchema adapter for live entities."""
    __regid__ = 'IJSONSchema'
    # Prevent this adapter from being selected in place of
    # IJSONSchemaRelatedEntityAdapter in case one picks a bad rtype/role.
    __select__ = non_final_entity() & ~match_kwargs('rtype', 'role')

    @property
    def etype(self):
        return self.entity.cw_etype

    def view_schema(self, **kwargs):
        """Return a JSON schema suitable for viewing adapted entity."""
        etype = self.entity.cw_etype
        relinfo = self.relinfo_for(VIEW_ROLE)
        jsldoc = build_document_tree(self._cw, etype, relinfo, VIEW_ROLE)
        return jsldoc.get_schema(**kwargs)

    def edition_schema(self, **kwargs):
        """Return a JSON schema suitable for editing adapted entity."""
        etype = self.entity.cw_etype
        relinfo = self.relinfo_for(EDITION_ROLE)
        jsldoc = build_document_tree(self._cw, etype, relinfo, EDITION_ROLE)
        return jsldoc.get_schema(**kwargs)

    def relinfo_for(self, schema_role):
        """Return a generator of relation information tuple (rtype, role,
        targettypes) for given schema role.
        """
        if schema_role == VIEW_ROLE:
            return visible_fields(self._cw, self.entity)
        elif schema_role == EDITION_ROLE:
            return editable_fields(self._cw, 'update', self.entity)
        else:
            raise ValueError('unhandled schema role "{0}" in {1}'.format(
                schema_role, self))

    def edit_entity(self, instance):
        """Return a CubicWeb entity built from `instance` data matching this
        JSON schema.
        """
        jsonschema_validate(self.edition_schema(), instance)
        values = {}
        for adapter, relation_mapper in self.iter_relation_mappers(EDITION_ROLE):
            values.update(relation_mapper.values(self.entity, instance))
        return self.entity.cw_set(**values)

    def serialize(self):
        """Return a dictionary of entity's data suitable for JSON
        serialization.
        """
        entity = self.entity
        entity.complete()
        etype = entity.cw_etype
        data = {
            'cw_etype': etype,
            'eid': entity.eid,
        }
        for relinfo in self._serializable_relinfo():
            relation_mapper = mapper_for_relation(self._cw, etype, *relinfo)
            value = relation_mapper.serialize(entity)
            if value is None:
                continue
            data[relation_mapper.orm_rtype] = value
        return data

    def _serializable_relinfo(self):
        """Yield (rtype, role, target_types) for fields to be included in the
        serialization of entity bound to this adapter.
        """
        rsection = self._cw.vreg['uicfg'].select(
            'primaryview_section', self._cw, entity=self.entity)
        eschema = self.entity.e_schema
        for rschema, tschemas, role in eschema.relation_definitions(True):
            if rschema in VIRTUAL_RTYPES:
                continue
            rtype = rschema.type
            if rschema.final:
                yield rtype, role, set([tschema.type for tschema in tschemas])
            else:
                target_types = set()
                for tschema in tschemas:
                    section = rsection.etype_get(eschema, rschema, role, tschema)
                    if section in ('attributes', 'relations'):
                        target_types.add(tschema.type)
                if target_types:
                    yield rtype, role, target_types


@objectify_predicate
def relation_for_entity(cls, cnx, entity, rtype, role):
    """Return 1 if `entity` has an `(rtype, role)` relation."""
    return 1 if entity.e_schema.has_relation(rtype, role) else 0


class IJSONSchemaRelatedEntityAdapter(IJSONSchemaEntityAdapter):
    """IJSONSchema adapter for entities in the context of a relation."""
    __select__ = (non_final_entity()
                  & match_kwargs('rtype', 'role') & relation_for_entity())

    @property
    def rtype(self):
        return self.cw_extra_kwargs['rtype']

    @property
    def role(self):
        return self.cw_extra_kwargs['role']

    def relinfo_for(self, schema_role):
        relinfo = super(IJSONSchemaRelatedEntityAdapter, self).relinfo_for(schema_role)
        return _filter_relinfo(relinfo, (self.rtype, self.role))

    def _serializable_relinfo(self):
        relinfo = super(IJSONSchemaRelatedEntityAdapter, self)._serializable_relinfo()
        return _filter_relinfo(relinfo, (self.rtype, self.role))
