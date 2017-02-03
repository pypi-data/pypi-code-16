# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2016 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Role Views
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model
from rattail.db.auth import has_permission, administrator_role, guest_role, authenticated_role

import formalchemy
from webhelpers.html import HTML, tags

from tailbone import forms
from tailbone.db import Session
from tailbone.views import MasterView
from tailbone.views.continuum import VersionView, version_defaults
from tailbone.newgrids import AlchemyGrid, GridAction


class PermissionsField(formalchemy.Field):
    """
    Custom field for role permissions.
    """

    def sync(self):
        if not self.is_readonly():
            role = self.model
            role.permissions = self.renderer.deserialize()


class RolesView(MasterView):
    """
    Master view for the Role model.
    """
    model_class = model.Role

    def configure_grid(self, g):
        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'
        g.default_sortkey = 'name'
        g.configure(
            include=[
                g.name,
            ],
            readonly=True)

    def configure_fieldset(self, fs):
        fs.append(PermissionsField('permissions'))
        permissions = self.request.registry.settings.get('tailbone_permissions', {})
        fs.permissions.set(renderer=forms.renderers.PermissionsFieldRenderer(permissions))
        fs.configure(
            include=[
                fs.name,
                fs.permissions,
            ])

    def template_kwargs_view(self, **kwargs):
        role = kwargs['instance']
        if role.users:

            # TODO: This is the first attempt at using a new grid outside of
            # the context of a primary master grid.  The API here is really
            # much hairier than I'd like...  Looks like we shouldn't need a key
            # for this one, for instance (no settings required), but there is
            # plenty of room for improvement here.
            users = sorted(role.users, key=lambda u: u.username)
            users = AlchemyGrid('roles.users', self.request, data=users, model_class=model.User,
                                main_actions=[
                                    GridAction('view', icon='zoomin',
                                               url=lambda r, i: self.request.route_url('users.view', uuid=r.uuid)),
                                ])
            users.configure(include=[users.username], readonly=True)
            kwargs['users'] = users

        else:
            kwargs['users'] = None
        kwargs['guest_role'] = guest_role(Session())
        kwargs['authenticated_role'] = authenticated_role(Session())
        return kwargs

    def before_delete(self, role):
        admin = administrator_role(Session())
        guest = guest_role(Session())
        authenticated = authenticated_role(Session())
        if role in (admin, guest, authenticated):
            self.request.session.flash("You may not delete the {} role.".format(role.name), 'error')
            return self.redirect(self.request.get_referrer(default=self.request.route_url('roles')))


class RoleVersionView(VersionView):
    """
    View which shows version history for a role.
    """
    parent_class = model.Role
    route_model_view = 'roles.view'


def includeme(config):
    RolesView.defaults(config)
    version_defaults(config, RoleVersionView, 'role')
