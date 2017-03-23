# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
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
Settings Views
"""

from __future__ import unicode_literals, absolute_import

import re

from rattail.db import model

from tailbone.views import MasterView


class SettingsView(MasterView):
    """
    Master view for the settings model.
    """
    model_class = model.Setting
    feedback = re.compile(r'^rattail\.mail\.user_feedback\..*')

    def configure_grid(self, g):
        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'
        g.default_sortkey = 'name'
        g.configure(
            include=[
                g.name,
                g.value,
            ],
            readonly=True)

    def configure_fieldset(self, fs):
        fs.configure(
            include=[
                fs.name,
                fs.value,
            ])
        if self.editing:
            fs.name.set(readonly=True)

    def editable_instance(self, setting):
        if self.rattail_config.demo():
            return not bool(self.feedback.match(setting.name))
        return True

    def deletable_instance(self, setting):
        if self.rattail_config.demo():
            return not bool(self.feedback.match(setting.name))
        return True


def includeme(config):
    SettingsView.defaults(config)
