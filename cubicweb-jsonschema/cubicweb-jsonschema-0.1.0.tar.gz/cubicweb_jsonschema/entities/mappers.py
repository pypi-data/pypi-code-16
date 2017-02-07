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
"""cubicweb-jsonschema entity type and relation mapper classes."""

from collections import OrderedDict

from six import text_type, string_types

import jsl

from logilab.common.decorators import cachedproperty
from logilab.common.registry import Predicate, objectify_predicate

from yams import BadSchemaDefinition
from cubicweb import neg_role
from cubicweb.predicates import match_kwargs
from cubicweb.view import Component

from cubicweb_jsonschema import CREATION_ROLE, EDITION_ROLE
from . import orm_rtype
from .ijsonschema import resource_identifier_schema, resource_identifier


@objectify_predicate
def yams_final_rtype(cls, cnx, etype, rtype, role, target_types):
    """Predicate that returns 1 when the supplied `rtype` is not final."""
    rdef = cnx.vreg.schema[etype].rdef(rtype, role=role, takefirst=True)
    if rdef.final:
        return 1
    return 0


@objectify_predicate
def yams_component_target(cls, cnx, etype, rtype, role, target_types):
    """Predicate that returns 1 when the target entity types are component of the relation defined
    by `rtype` and `role` (i.e. the relation has composite set to `role`).
    """
    component = None
    eschema = cnx.vreg.schema[etype]
    for target_type in target_types:
        rdef = eschema.rdef(rtype, role=role, targettype=target_type)
        _component = rdef.composite == role
        if component is None:
            component = _component
        elif not component == _component:
            cls.warning('component inconsistency accross target types')
            return 0
    return component


class yams_match(Predicate):
    """Predicate that returns 1 when the supplied relation match parameters given as predicate
    argument.
    """

    def __init__(self, etype=None, rtype=None, role=None, target_types=()):
        self.etype = etype
        self.rtype = rtype
        self.role = role
        if isinstance(target_types, string_types):
            target_types = {target_types}
        elif not isinstance(target_types, (set, frozenset)):
            target_types = frozenset(target_types)
        self.target_types = target_types

    def __call__(self, cls, cnx, etype, rtype, role, target_types, **kwargs):
        for key in ('etype', 'rtype', 'role'):
            expected = getattr(self, key, None)
            if expected is not None and locals()[key] != expected:
                return 0
        if (self.target_types
                and not set(target_types).issubset(self.target_types)):
            return 0
        return 1


def base_fields(etype):
    fields = OrderedDict()
    fields['__etype__'] = jsl.fields.StringField(
        required=True, enum=[etype], default=etype)
    fields['__eid__'] = jsl.fields.StringField(required=True)
    return fields


def default_options(_cw, etype):
    """Return an Options class for a jsl.Document named `etype`."""
    attrs = {
        'definition_id': etype,
        'title': _cw._(etype),
    }
    return type('Options', (object,), attrs)


class ETypeMapper(Component):
    """A mapper component to build JSL document for an entity type."""
    __regid__ = 'jsonschema.map.etype'
    __select__ = match_kwargs('etype')

    # Should "base" fields __etype__/__eid__ be included in main schema
    # document?
    include_base_fields = False

    # Extra fields to be inserted in the main document of the JSON schema;
    # defined as a 2-tuple mapping either a field name to a JSL field instance
    # or a relation type to a dict with extra configuration for the generated
    # JSL field.
    fields = ()

    @property
    def etype(self):
        return self.cw_extra_kwargs['etype']

    def jsl_document(self, relinfo, schema_role=None):
        """Return a jsl.Document for `etype` with fields built from `relinfo`
        relation information along with a dict mapping (rtype, role) to target
        entity types obtained from processing `relinfo`.
        """
        attrs = OrderedDict()
        if self.include_base_fields:
            attrs.update(base_fields(self.etype))
        relation_targets = {}
        fields = dict(self.fields)
        for rtype, role, target_types in relinfo:
            kwargs = {}
            field_value = fields.get(rtype)
            if isinstance(field_value, dict):
                # When field value is a dict, it is meant as extra
                # configuration to the respective JSL field.
                kwargs = field_value
                # We then do not want it when processing `fields` below.
                del fields[rtype]
            mapper = self._relation_mapper(rtype, role, target_types)
            attrs[rtype] = mapper.jsl_field(schema_role, **kwargs)
            relation_targets[rtype, role] = mapper.target_types
        for rtype, value in fields.items():
            assert isinstance(value, jsl.fields.BaseField), \
                'explicit field "{0}" must be a jsl.BaseField'.format(rtype)
            attrs[rtype] = value
        attrs['Options'] = default_options(self._cw, self.etype)
        return type(str(self.etype), (jsl.Document, ), attrs), relation_targets

    def _relation_mapper(self, rtype, role, target_types=None):
        if target_types is None:
            rschema = self._cw.vreg.schema[rtype]
            target_types = {t.type for t in rschema.targets(self.etype, role)}
        assert isinstance(target_types, set), target_types
        return self._cw.vreg['components'].select(
            'jsonschema.map.relation', self._cw,
            etype=self.etype, rtype=rtype, role=role, target_types=target_types)


class _BaseRelationMapper(Component):
    """Base abstract class to fill the gap between a yams relation and it's json
    schema mapping.

    They should be selected depending on the relation (`etype`, `rtype`, `role`
    and optionaly `target_types`). You may then get a Jsl field from them by
    calling the `jsl_field` method.

    Concrete classes must supply a `jsl_field_class` attribute (see its doc
    below).

    Attributes defined here are:

    * `etype`, `rtype` and `role` define the relation on which this mapper operates;

    * `target_types` indicates the possible target types at the end of the relation (empty for
      attribute relations).
    """

    __regid__ = 'jsonschema.map.relation'
    __select__ = match_kwargs('etype', 'rtype', 'role')
    __abstract__ = True

    @property
    def jsl_field_class(self):
        """Return the jsl.fields.BaseField child class to be returned by the
        factory.
        """
        raise NotImplementedError

    def __init__(self, _cw, **kwargs):
        self.etype = kwargs.pop('etype')
        self.rtype = kwargs.pop('rtype')
        self.role = kwargs.pop('role')
        self.target_types = []
        rschema = _cw.vreg.schema[self.rtype]
        target_types = kwargs.pop('target_types', None)
        for target_eschema in sorted(rschema.targets(role=self.role)):
            if target_eschema.final:
                continue
            target_type = target_eschema.type
            if target_types is not None and target_type not in target_types:
                continue
            self.target_types.append(target_type)

        super(_BaseRelationMapper, self).__init__(_cw, **kwargs)

    def __repr__(self):
        return ('<{0.__class__.__name__} etype={0.etype} rtype={0.rtype} '
                'role={0.role} target_types={0.target_types}>'.format(self))

    @cachedproperty
    def description(self):
        eschema = self._cw.vreg.schema[self.etype]
        rdef = eschema.rdef(self.rtype, role=self.role, takefirst=True)
        if rdef.description:
            return self._cw._(rdef.description)

    @cachedproperty
    def title(self):
        if self.role == 'object':
            return self._cw._(self.rtype + '_object')
        return self._cw._(self.rtype)

    @cachedproperty
    def orm_rtype(self):
        return orm_rtype(self.rtype, self.role)

    def jsl_field(self, schema_role, **kwargs):
        if 'title' not in kwargs:
            kwargs['title'] = self.title
        if 'description' not in kwargs and self.description is not None:
            kwargs['description'] = self.description
        kwargs.pop('module', None)
        return self.jsl_field_class(**kwargs)

    def values(self, entity, instance):
        """Return a dictionary holding deserialized value for this field, given the input
        entity (None on creation) and `instance` (JSON values as dictionary).
        """
        if self.rtype in instance:
            return {self.orm_rtype: self._type(instance[self.rtype])}
        return {}

    def serialize(self, entity):
        """Return the serialized value for this field."""
        raise NotImplementedError()

    @staticmethod
    def _type(json_value):
        """Return properly typed value for use within a cubicweb's entity from given JSON value.

        Nothing to do by default.
        """
        return json_value


class _AttributeMapper(_BaseRelationMapper):
    __abstract__ = True
    __select__ = yams_final_rtype()

    @property
    def attr(self):
        return self._cw.vreg.schema[self.etype].rdef(self.rtype)

    def add_constraint(self, cstr, jsl_attrs):
        serializer = self._cw.vreg['components'].select_or_none(
            'jsonschema.map.constraint', self._cw.vreg, self._cw._,
            self.etype, self.rtype, cstr, jsl_attrs)
        if serializer is not None:
            new_attrs = serializer.todict()
            if new_attrs:
                jsl_attrs.update(new_attrs)
        else:
            self.warning('JSL: ignored %s on %s', cstr.type(), self.attr)

    def jsl_field(self, schema_role, **kwargs):
        if schema_role in (CREATION_ROLE, EDITION_ROLE):
            if 'required' not in kwargs and self.attr.cardinality[0] == '1':
                kwargs['required'] = True
            if 'default' not in kwargs and self.attr.default is not None:
                kwargs['default'] = self.attr.default
            for constraint in self.attr.constraints:
                self.add_constraint(constraint, kwargs)
        return super(_AttributeMapper, self).jsl_field(schema_role, **kwargs)

    def serialize(self, entity):
        value = getattr(entity, self.orm_rtype)
        if value is not None:
            return self._type(value)


class StringField(jsl.fields.StringField):
    """String field handling vocabulary as enum."""

    def __init__(self, **kwargs):
        super(StringField, self).__init__(**kwargs)
        if 'enum' in kwargs:
            self.enum_titles = kwargs['enum_titles']

    def get_definitions_and_schema(self, **kwargs):
        definitions, schema = super(
            StringField, self).get_definitions_and_schema(**kwargs)
        if 'enum' not in schema:
            return definitions, schema
        if 'options' not in schema:
            schema['options'] = {}
        schema['options']['enum_titles'] = self.enum_titles
        return definitions, schema


class StringMapper(_AttributeMapper):
    __select__ = yams_match(target_types='String')
    jsl_field_class = StringField
    _type = text_type


class FloatMapper(_AttributeMapper):
    __select__ = yams_match(target_types='Float')
    jsl_field_class = jsl.fields.NumberField


class IntMapper(_AttributeMapper):
    __select__ = yams_match(target_types='Int')
    jsl_field_class = jsl.fields.IntField


class BooleanMapper(_AttributeMapper):
    __select__ = yams_match(target_types='Boolean')
    jsl_field_class = jsl.fields.BooleanField


class PasswordMapper(_AttributeMapper):
    __select__ = yams_match(target_types='Password')
    jsl_field_class = jsl.fields.StringField

    def jsl_field(self, schema_role, **kwargs):
        if schema_role == EDITION_ROLE:
            kwargs.setdefault('required', False)
        return super(PasswordMapper, self).jsl_field(schema_role, **kwargs)

    def serialize(self, entity):
        return None


class DateMapper(_AttributeMapper):
    __select__ = yams_match(target_types=('Date'))
    jsl_field_class = jsl.fields.StringField

    def jsl_field(self, *args, **kwargs):
        kwargs.setdefault('format', 'date')
        return super(_AttributeMapper, self).jsl_field(*args, **kwargs)


class DatetimeMapper(_AttributeMapper):
    __select__ = yams_match(target_types=('Datetime', 'TZDatetime'))
    jsl_field_class = jsl.fields.StringField

    def jsl_field(self, *args, **kwargs):
        kwargs.setdefault('format', 'date-time')
        return super(_AttributeMapper, self).jsl_field(*args, **kwargs)


class BytesMapper(_AttributeMapper):
    __select__ = yams_match(target_types='Bytes')
    jsl_field_class = jsl.fields.StringField

    def jsl_field(self, *args, **kwargs):
        kwargs.setdefault('format', 'data-url')
        return super(BytesMapper, self).jsl_field(*args, **kwargs)


class _RelationMapper(_BaseRelationMapper):
    """Abstract class for true relation (as opposed to attribute) mapper.
    """
    __abstract__ = True
    __select__ = ~yams_final_rtype()
    jsl_field_class = jsl.fields.ArrayField

    def jsl_field(self, schema_role, **kwargs):
        if 'items' not in kwargs:
            targets = list(self.jsl_field_targets())
            cardinalities = set([])
            rschema = self._cw.vreg.schema[self.rtype]
            for target_type in self.target_types:
                rdef = rschema.role_rdef(
                    self.etype, target_type, self.role)
                cardinalities.add(rdef.role_cardinality(self.role))
            if len(targets) > 1:
                kwargs['items'] = jsl.fields.OneOfField(targets)
            else:
                kwargs['items'] = targets[0]
            if schema_role in (CREATION_ROLE, EDITION_ROLE):
                cardinality = cardinalities.pop()
                if cardinalities:
                    raise BadSchemaDefinition(
                        'inconsistent cardinalities within {0} relation '
                        'definitions'.format(self.rtype))
                if cardinality != '*':
                    if 'min_items' not in kwargs:
                        kwargs['min_items'] = 0 if cardinality in '?' else 1
                    if 'max_items' not in kwargs and cardinality in '?1':
                        kwargs['max_items'] = 1
        return super(_RelationMapper, self).jsl_field(schema_role, **kwargs)

    def jsl_field_targets(self):
        """Return an iterator on jsl field objects to put in the 'items' key."""
        raise NotImplementedError()


class InlinedRelationMapper(_RelationMapper):
    """Map relation as 'inlined', i.e. the target of the relation is created/edited along with its
    original entity.
    """
    __select__ = _RelationMapper.__select__ & yams_component_target()

    def jsl_field_targets(self):
        for target_type in self.target_types:
            yield jsl.fields.DocumentField(target_type, as_ref=True)

    def values(self, entity, instance):
        if self.rtype in instance:
            # Would require knownledge of the target type from "instance",
            # but the generated JSON schema does not expose this yet.
            assert len(self.target_types) == 1, \
                'cannot handle multiple target types yet: {}'.format(self.target_types)
            adapted = self._cw.vreg['adapters'].select(
                'IJSONSchema', self._cw, etype=self.target_types[0])
            if entity is not None:
                # if entity already exists, delete entities related through this mapped relation
                for linked_entity in getattr(entity, self.orm_rtype):
                    if linked_entity.cw_etype in self.target_types:
                        linked_entity.cw_delete()
            result = []
            for subinstance in instance[self.rtype]:
                result.append(adapted.create_entity(subinstance))
            return {self.rtype: result}
        return {}

    def serialize(self, entity):
        rset = entity.related(
            self.rtype, self.role, targettypes=tuple(self.target_types))
        if not rset:
            return None

        def adapt(entity):
            return self._cw.vreg['adapters'].select(
                'IJSONSchema', self._cw, entity=entity,
                rtype=self.rtype, role=neg_role(self.role))

        return [adapt(related).serialize() for related in rset.entities()]


class RelationMapper(_RelationMapper):
    """Map relation as 'generic', i.e. the target of the relation may be selected in preexisting
    possible targets..
    """
    __select__ = _RelationMapper.__select__ & ~yams_component_target()

    def jsl_field_targets(self):
        yield resource_identifier_schema()

    def values(self, entity, instance):
        if self.rtype in instance:
            if entity is not None:
                entity.cw_set(**{self.orm_rtype: None})
            result = []
            for subinstance in instance[self.rtype]:
                result.append(subinstance['id'])
            return {self.rtype: result}
        return {}

    def serialize(self, entity):
        rset = entity.related(
            self.rtype, self.role, targettypes=tuple(self.target_types))
        if not rset:
            return None
        return [resource_identifier(related) for related in rset.entities()]
