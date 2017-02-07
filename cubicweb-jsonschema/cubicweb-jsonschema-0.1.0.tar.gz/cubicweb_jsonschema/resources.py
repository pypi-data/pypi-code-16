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

"""cubicweb-jsonschema Pyramid resources definition."""

from pyramid.decorator import reify
from cubicweb.pyramid.resources import ETypeResource


class ApplicationSchema(object):
    """The root schema resource, describing the application schema."""
    __name__ = ''
    __parent__ = None

    def __init__(self, request):
        self.request = request

    def __getitem__(self, value):
        vreg = self.request.registry['cubicweb.registry']
        try:
            etype = vreg.case_insensitive_etypes[value.lower()]
        except KeyError:
            raise KeyError(value)
        return ETypeSchema(self.request, etype, self)


class _SchemaResource(object):

    @reify
    def rset(self):
        return self.described_resource.rset


class ETypeSchema(_SchemaResource):
    """Schema resource for an entity type."""

    def __init__(self, request, etype, parent):
        self.request = request
        self.etype = etype
        self.__name__ = etype.lower()
        self.__parent__ = parent

    def __repr__(self):
        return '<{module}.{self.__class__.__name__} for {self.etype} entity type>'.format(
            self=self, module=__name__)

    def __getitem__(self, value):
        entity_resource = self.described_resource[value]
        entity_resource.__parent__ = self.described_resource
        entity_resource.__name__ = value
        return EntitySchema(self.request, entity_resource, self)

    @reify
    def described_resource(self):
        """The resource described by the schema bound to this resource."""
        resource = ETypeResource(self.request, self.etype)
        parent = type('RootResource', (object, ), {'__parent__': None, '__name__': ''})()
        resource.__parent__ = parent
        resource.__name__ = self.etype.lower()
        return resource


class EntitySchema(_SchemaResource):
    """Schema resource for an entity."""

    def __init__(self, request, entity_resource, parent):
        self.request = request
        self.described_resource = entity_resource
        self.__parent__ = parent
        self.__name__ = entity_resource.__name__

    def __repr__(self):
        return '<{module}.{self.__class__.__name__} describing {self.described_resource}>'.format(
            self=self, module=__name__)
