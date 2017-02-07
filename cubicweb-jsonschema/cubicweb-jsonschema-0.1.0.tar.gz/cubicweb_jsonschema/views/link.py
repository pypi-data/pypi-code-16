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

"""cubicweb-jsonschema hyper schema "link" components.

See http://json-schema.org/draft-04/links for the JSON schema of these
objects.
"""


from cubicweb.appobject import AppObject
from cubicweb.predicates import (has_add_permission, has_permission,
                                 match_kwargs)

from .. import VIEW_ROLE, CREATION_ROLE, EDITION_ROLE


class Link(AppObject):
    """Abstract hyper schema link."""
    __registry__ = 'links'

    def description_object(self, request, resource):
        """Return the link description object as a dict."""
        raise NotImplementedError()


class ETypeLink(Link):
    """Abstract hyper schema link suitable for entity type JSON schema."""
    __abstract__ = True
    __select__ = match_kwargs('etype')

    @property
    def etype(self):
        return self.cw_extra_kwargs['etype']


class EntitiesLink(ETypeLink):
    """Link for entities of selected type."""
    __regid__ = 'entities'

    def description_object(self, request, resource):
        description = self._cw._('List {0}').format(
            self._cw.__(self.etype + '_plural').lower())
        return {
            u'description': description,
            u'href': request.resource_path(resource.described_resource),
            u'method': u'GET',
            u'rel': u'instances',
            u'targetSchema': {
                u'$ref': request.resource_path(resource, 'schema'),
            },
            u'title': u'List',
        }


class EntityFromIdViewLink(ETypeLink):
    """Link for viewing a given entity."""
    __regid__ = 'entity.view-from-id'

    def description_object(self, request, resource):
        description = self._cw._('View a {0} entity').format(self.etype)
        return {
            u'description': description,
            u'href': request.resource_path(resource.described_resource, '{id}'),
            u'method': u'GET',
            u'rel': u'self',
            u'targetSchema': {
                '$ref': request.resource_path(
                    resource, 'schema', query={'role': VIEW_ROLE}),
            },
            u'title': u'View',
        }


class AddEntityLink(ETypeLink):
    """Link for adding an entity of selected type."""
    __regid__ = 'entity.add'
    __select__ = ETypeLink.__select__ & has_add_permission()

    def description_object(self, request, resource):
        description = self._cw._('Create a {0} entity').format(self.etype)
        return {
            u'description': description,
            u'href': request.resource_path(resource.described_resource),
            u'method': u'POST',
            u'rel': u'create',
            u'schema': {
                u'$ref': request.resource_path(
                    resource, 'schema', query={'role': CREATION_ROLE}),
            },
            u'title': u'Create',
        }


class EntityLink(Link):
    """Abstract hyper schema link suitable for entity JSON schema."""
    __abstract__ = True
    __select__ = match_kwargs('entity')

    @property
    def entity(self):
        return self.cw_extra_kwargs['entity']


class EntityViewLink(EntityLink):
    """Link for viewing an entity."""
    __regid__ = 'entity.view'
    __select__ = EntityLink.__select__ & has_permission('read')

    def description_object(self, request, resource):
        entity = self.entity
        description = self._cw._('View {0} #{1}').format(
            self._cw.__(entity.cw_etype), entity.eid)
        return {
            u'description': description,
            u'href': request.resource_path(resource.described_resource),
            u'method': u'GET',
            u'rel': u'self',
            u'title': u'View',
            u'targetSchema': {
                u'$ref': request.resource_path(
                    resource, 'schema', query={'role': VIEW_ROLE}),
            },
        }


class EntityUpdateLink(EntityLink):
    """Link for updating an entity."""
    __regid__ = 'entity.update'
    __select__ = EntityLink.__select__ & has_permission('update')

    def description_object(self, request, resource):
        entity = self.entity
        description = self._cw._('Update {0} #{1}').format(
            self._cw.__(entity.cw_etype), entity.eid)
        return {
            u'description': description,
            u'href': request.resource_path(resource.described_resource),
            u'method': u'PATCH',
            u'rel': u'edit',
            u'title': u'Edit',
            u'schema': {
                u'$ref': request.resource_path(
                    resource, 'schema', query={'role': EDITION_ROLE}),
            },
        }


class EntityDeleteLink(EntityLink):
    """Link for deleting an entity."""
    __regid__ = 'entity.delete'
    __select__ = EntityLink.__select__ & has_permission('delete')

    def description_object(self, request, resource):
        entity = self.entity
        description = self._cw._('Delete {0} #{1}').format(
            self._cw.__(entity.cw_etype), entity.eid)
        return {
            u'description': description,
            u'href': request.resource_path(resource.described_resource),
            u'method': u'DELETE',
            u'rel': u'delete',  # XXX no sure about this?
            u'title': u'Delete',
        }


class EntityParentLink(EntityLink):
    """Link to the parent resource of an entity (i.e. the entity type)."""
    __regid__ = 'entity.type'

    def description_object(self, request, resource):
        entity = self.entity
        description = self._cw._('Entities of type {0}').format(entity.cw_etype)
        return {
            u'description': description,
            u'href': request.resource_path(resource.__parent__.described_resource),
            u'method': u'GET',
            u'rel': u'up',
            u'title': self._cw.__('{0}_plural').format(entity.cw_etype),
            u'targetSchema': {
                u'$ref': request.resource_path(
                    resource.__parent__, 'schema'),
            },
        }
