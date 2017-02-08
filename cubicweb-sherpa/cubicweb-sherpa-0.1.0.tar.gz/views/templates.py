# -*- coding: utf-8
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
"""sherpa views/templates"""

from logilab.common.decorators import monkeypatch

from cubicweb.utils import HTMLHead, UStringIO
from cubicweb.web.views import basetemplates

from . import jinja_render


# Bootstrap configuration.
basetemplates.TheMainTemplate.twbs_container_cls = 'container-fluid'


@monkeypatch(HTMLHead)
def add_onload(self, jscode):
    """original `add_onload` implementation use `$(cw)`
    but `cw` variable is not available
    in francearchive, use `$` instead"""
    self.add_post_inline_script(u"""$(function() {
  %s
});""" % jscode)


class SherpaMainTemplate(basetemplates.TheMainTemplate):

    def call(self, view):
        self.set_request_content_type()
        self.write_doctype()
        self.template_header(self.content_type, view=view)
        context = self.template_context(view)
        self.w(jinja_render('maintemplate', **context))

    def template_context(self, view):
        """Return the main-template's context."""
        # left boxes
        left_boxes = list(self._cw.vreg['ctxcomponents'].poss_visible_objects(
            self._cw, rset=self.cw_rset, view=view, context='left'))
        stream = UStringIO()
        for box in left_boxes:
            box.render(w=stream.write, view=view)
        left_boxes_html = stream.getvalue()
        # header
        stream = UStringIO()
        w = stream.write
        components = self.get_components(view, context='header-right')
        if components:
            w(u'<ul class="nav navbar-nav navbar-right">')
            for component in components:
                w(u'<li>')
                component.render(w=w)
                w(u'</li>')
            w(u'</ul>')
        right_header_component = stream.getvalue()
        # breadcrumbs
        stream = UStringIO()
        w = stream.write
        components = self.get_components(view, context='header-center')
        if components:
            for component in components:
                component.render(w=w)
        breadcrumbs = stream.getvalue()

        ctx = self.base_context()
        url = self._cw.build_url
        ctx.update({
            'title': view.page_title(),
            'page_content': view.render(),
            'breadcrumbs': breadcrumbs,
            'right_header_component': right_header_component,
            'left_boxes': left_boxes_html,
            'side_box': {
                'resources': [
                    {'url': url('shema_seda'),
                     'label': u'Schéma du SEDA 2.0'},
                    {'url': url('dictionnaire'),
                     'label': 'Dictionnaire des balises'},
                    {'url': url('documentation_fonctionnelle'),
                     'label': 'Documentation fonctionnelle'},
                    {'url': url('documentation_technique'),
                     'label': 'Documentation technique'},
                ],
                'goTo_links': [
                    {'url': url('SEDAArchiveUnit'),
                     'label': u"Unités d'archive"},
                    {'url': url('SEDAArchiveTransfer'),
                     'label': 'Profils SEDA'}
                ],
                'navigation_Link': [
                    {'url': url('project'),
                     'label': 'Le projet Sherpa'},
                    {'url': url('utilisation'),
                     'label': "Mode d'emploi"},
                    {'url': url('seda'),
                     'label': "Le SEDA"},
                ]
            },
            'footer': {
                'copyright': '### copyright ###',
                'contact': 'mailto:#'
            },
        })
        ctx.update(getattr(view, 'template_context', lambda: {})())

        return ctx

    def base_context(self):
        """Return a basic context using standard cubicweb information."""
        req = self._cw
        return {
            'page_id': 'contentmain',
            '_': req._,
            'user': req.user.login,
            'base_url': req.build_url(''),
            'data_url': req.datadir_url,
            'current_url': req.relative_path(),
        }


def registration_callback(vreg):
    vreg.register_and_replace(SherpaMainTemplate, basetemplates.TheMainTemplate)
