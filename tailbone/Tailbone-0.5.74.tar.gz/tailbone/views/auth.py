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
Auth Views
"""

from __future__ import unicode_literals, absolute_import

from rattail.db.auth import authenticate_user, set_user_password

import formencode as fe
from pyramid.httpexceptions import HTTPForbidden
from pyramid.security import remember, forget
from pyramid_simpleform import Form
from webhelpers.html import tags, literal

from tailbone import forms
from tailbone.db import Session
from tailbone.views import View


class UserLogin(fe.Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    username = fe.validators.NotEmpty()
    password = fe.validators.NotEmpty()


class CurrentPasswordCorrect(fe.validators.FancyValidator):

    def _to_python(self, value, state):
        user = state
        if not authenticate_user(Session, user.username, value):
            raise fe.Invalid("The password is incorrect.", value, state)
        return value


class ChangePassword(fe.Schema):

    allow_extra_fields = True
    filter_extra_fields = True

    current_password = fe.All(
        fe.validators.NotEmpty(),
        CurrentPasswordCorrect())

    new_password = fe.validators.NotEmpty()
    confirm_password = fe.validators.NotEmpty()

    chained_validators = [fe.validators.FieldsMatch(
            'new_password', 'confirm_password')]


class AuthenticationView(View):

    def forbidden(self):
        """
        Access forbidden view.

        This is triggered whenever access is not allowed for an otherwise
        appropriate view.
        """
        msg = literal("You do not have permission to do that.")
        if not self.request.authenticated_userid:
            msg += literal("&nbsp; (Perhaps you should %s?)" %
                           tags.link_to("log in", self.request.route_url('login')))
            # Store current URL in session, for smarter redirect after login.
            self.request.session['next_url'] = self.request.current_route_url()
        self.request.session.flash(msg, allow_duplicate=False)
        return self.redirect(self.request.get_referrer())

    def login(self, mobile=False):
        """
        The login view, responsible for displaying and handling the login form.
        """
        home = 'mobile.home' if mobile else 'home'
        referrer = self.request.get_referrer(default=self.request.route_url(home))

        # redirect if already logged in
        if self.request.user:
            self.request.session.flash("{} is already logged in".format(self.request.user), 'error')
            return self.redirect(referrer)

        form = forms.SimpleForm(self.request, UserLogin)
        if form.validate():
            user = authenticate_user(Session(),
                                     form.data['username'],
                                     form.data['password'])
            if user:
                # okay now they're truly logged in
                headers = remember(self.request, user.uuid)
                # treat URL from session as referrer, if available
                referrer = self.request.session.pop('next_url', referrer)
                return self.redirect(referrer, headers=headers)
            else:
                self.request.session.flash("Invalid username or password", 'error')

        return {
            'form': forms.FormRenderer(form),
            'referrer': referrer,
            'dialog': mobile,
        }

    def mobile_login(self):
        return self.login(mobile=True)

    def logout(self, mobile=False):
        """
        View responsible for logging out the current user.

        This deletes/invalidates the current session and then redirects to the
        login page.
        """
        self.request.session.delete()
        self.request.session.invalidate()
        headers = forget(self.request)
        login = 'mobile.login' if mobile else 'login'
        referrer = self.request.get_referrer(default=self.request.route_url(login))
        return self.redirect(referrer, headers=headers)

    def mobile_logout(self):
        return self.logout(mobile=True)

    def change_password(self):
        """
        Allows a user to change his or her password.
        """
        if not self.request.user:
            return self.redirect(self.request.route_url('home'))

        form = Form(self.request, schema=ChangePassword, state=self.request.user)
        if form.validate():
            set_user_password(self.request.user, form.data['new_password'])
            return self.redirect(self.request.get_referrer())

        return {'form': forms.FormRenderer(form)}

    def become_root(self):
        """
        Elevate the current request to 'root' for full system access.
        """
        if not self.request.is_admin:
            raise HTTPForbidden()
        self.request.session['is_root'] = True
        self.request.session.flash("You have been elevated to 'root' and now have full system access")
        return self.redirect(self.request.get_referrer())

    def stop_root(self):
        """
        Lower the current request from 'root' back to normal access.
        """
        if not self.request.is_admin:
            raise HTTPForbidden()
        self.request.session['is_root'] = False
        self.request.session.flash("Your normal system access has been restored")
        return self.redirect(self.request.get_referrer())

    @classmethod
    def defaults(cls, config):

        # forbidden
        config.add_forbidden_view(cls, attr='forbidden')

        # login
        config.add_route('login', '/login')
        config.add_view(cls, attr='login', route_name='login', renderer='/login.mako')
        config.add_route('mobile.login', '/mobile/login')
        config.add_view(cls, attr='mobile_login', route_name='mobile.login', renderer='/mobile/login.mako')

        # logout
        config.add_route('logout', '/logout')
        config.add_view(cls, attr='logout', route_name='logout')
        config.add_route('mobile.logout', '/mobile/logout')
        config.add_view(cls, attr='mobile_logout', route_name='mobile.logout')

        # change password
        config.add_route('change_password', '/change-password')
        config.add_view(cls, attr='change_password', route_name='change_password', renderer='/change_password.mako')

        # become/stop root
        config.add_route('become_root', '/root/yes')
        config.add_view(cls, attr='become_root', route_name='become_root')
        config.add_route('stop_root', '/root/no')
        config.add_view(cls, attr='stop_root', route_name='stop_root')


def includeme(config):
    AuthenticationView.defaults(config)
