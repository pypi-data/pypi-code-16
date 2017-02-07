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

from pyramid import httpexceptions
from pyramid.view import view_config

from cubicweb.web.views import uicfg

from . import VIEW_ROLE, CREATION_ROLE, EDITION_ROLE
from .entities.ijsonschema import collection_schema
from . import resources


JSONSCHEMA_MEDIA_TYPE = 'application/schema+json'


def jsonschema_config(**settings):
    for name, value in [
        ('name', 'schema'),
        ('route_name', 'cubicweb-jsonschema'),
        ('accept', JSONSCHEMA_MEDIA_TYPE),
        ('renderer', 'json'),
        ('request_method', 'GET'),
    ]:
        settings.setdefault(name, value)
    return view_config(**settings)


@jsonschema_config(context=resources.ApplicationSchema)
def application_schema(context, request):
    """Schema view for the application."""
    vreg = request.registry['cubicweb.registry']

    def links():
        for eschema in vreg.schema.entities():
            if uicfg.indexview_etype_section.get(eschema) != 'application':
                continue
            etype = eschema.type
            etype_resource = context[etype]
            possible_links = vreg['links'].possible_objects(
                request.cw_request, etype=etype)
            for link in possible_links:
                yield link.description_object(request, etype_resource)

    return {'links': list(links())}


@jsonschema_config(context=resources.ETypeSchema, request_param='role')
def etype_role_schema(context, request):
    """Schema view for an entity type with specified role."""
    req = request.cw_request
    adapted = req.vreg['adapters'].select('IJSONSchema', req,
                                          etype=context.etype)
    role = request.params['role'].lower()
    if role == VIEW_ROLE:
        return adapted.view_schema(ordered=True)
    elif role == CREATION_ROLE:
        return adapted.creation_schema(ordered=True)
    else:
        raise httpexceptions.HTTPBadRequest(
            'invalid role: {0}'.format(role))


@jsonschema_config(context=resources.ETypeSchema)
def etype_schema(context, request):
    """Schema view for an entity type returning the complete hyper schema.
    """
    req = request.cw_request
    name = '{0}_plural'.format(context.etype)
    title = req._(name)
    schema = collection_schema(name, title, ordered=True)
    vreg = request.registry['cubicweb.registry']
    schema['links'] = [
        link.description_object(request, context)
        for link in vreg['links'].possible_objects(req, etype=context.etype,
                                                   rset=context.rset)
    ]
    return schema


@jsonschema_config(context=resources.EntitySchema, request_param='role')
def entity_role_schema(context, request):
    """Schema view for a live entity with specified role."""
    entity = context.rset.one()  # May raise HTTPNotFound.
    adapted = entity.cw_adapt_to('IJSONSchema')
    role = request.params['role'].lower()
    if role == VIEW_ROLE:
        return adapted.view_schema(ordered=True)
    elif role == EDITION_ROLE:
        return adapted.edition_schema(ordered=True)
    else:
        raise httpexceptions.HTTPBadRequest(
            'invalid role: {0}'.format(role))


@jsonschema_config(context=resources.EntitySchema)
def entity_schema(context, request):
    """Schema view for a live entity returning the complete hyper schema.
    """
    req = request.cw_request
    entity = context.rset.one()  # May raise HTTPNotFound.
    adapted = entity.cw_adapt_to('IJSONSchema')
    schema = adapted.view_schema(ordered=True)
    vreg = request.registry['cubicweb.registry']
    schema['links'] = [
        link.description_object(request, context)
        for link in vreg['links'].possible_objects(req, entity=entity)
    ]
    return schema


def includeme(config):
    config.include('.predicates')
    config.add_route(
        'cubicweb-jsonschema',
        '*traverse',
        factory=resources.ApplicationSchema,
        strict_accept=JSONSCHEMA_MEDIA_TYPE,
    )
    config.scan(__name__)
