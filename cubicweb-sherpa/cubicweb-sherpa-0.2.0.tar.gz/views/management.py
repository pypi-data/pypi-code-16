# copyright 2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

from logilab.mtconverter import xml_escape

from cubicweb.predicates import relation_possible, one_line_rset, non_final_entity
from cubicweb.web import action, formwidgets
from cubicweb.web.formfields import guess_field
from cubicweb.web.views import actions, management

from cubes.relationwidget.views import RelationFacetWidget


class SherpaSecurityManagementView(management.SecurityManagementView):
    """Security view overriden to hide permissions definitions and using a
    RelationFacetWidget to edit owner"""
    __select__ = (management.SecurityManagementView.__select__ &
                  relation_possible('owned_by', action='add'))

    def entity_call(self, entity):
        w = self.w
        w(u'<h1><span class="etype">%s</span> <a href="%s">%s</a></h1>'
          % (entity.dc_type().capitalize(),
             xml_escape(entity.absolute_url()),
             xml_escape(entity.dc_title())))
        w('<h2>%s</h2>' % self._cw.__('Manage security'))
        msg = self._cw.__('ownerships have been changed')
        form = self._cw.vreg['forms'].select(
            'base', self._cw, entity=entity,
            form_renderer_id='base', submitmsg=msg,
            form_buttons=[formwidgets.SubmitButton()],
            domid='ownership%s' % entity.eid,
            __redirectvid='security',
            __redirectpath=entity.rest_path())
        field = guess_field(entity.e_schema,
                            self._cw.vreg.schema['owned_by'],
                            req=self._cw,
                            widget=RelationFacetWidget())
        field.help = None
        form.append_field(field)
        form.render(w=w, display_progress_div=False)


actions.ManagePermissionsAction.__select__ = (
    action.Action.__select__ & one_line_rset() & non_final_entity()
    & relation_possible('owned_by', action='add'))


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__)
    vreg.unregister(management.SecurityManagementView)
