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
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

from jinja2 import Environment, PackageLoader

from cubicweb import _
from cubicweb.view import View
from cubicweb.web.views import urlrewrite, startup

_JINJA_ENV = Environment(loader=PackageLoader('cubes.sherpa.views'))


def jinja_render(template_name, **ctx):
    """Return a string containing result of rendering of Jinja2's `template_name` with
    `ctx` as context.
    """
    template = _JINJA_ENV.get_template(template_name + '.jinja2')
    return template.render(**ctx)


class JinjaStaticView(View):
    """Abstract base class to render static pages from a jinja template."""
    __abstract__ = True
    template_name = None
    title = None

    def call(self, **kw):
        self.w(jinja_render(self.template_name,
                            title=self._cw._(self.title),
                            data_url=self._cw.datadir_url))


def jinja_static_view(template_name, title=None):
    """Generate a sub-class of JinjaStaticView parametrized with its `template_name` and `title`.

    `__regid__` is built by prepending 'sherpa.' to template_name.
    """
    class_name = template_name.capitalize() + 'View'
    regid = 'sherpa.' + template_name
    if (template_name == 'index') :
        regid = 'index'

    return type(class_name, (JinjaStaticView,), {'__regid__': regid,
                                                 'template_name': template_name,
                                                 'title': title})


ProjectView = jinja_static_view('project', 'Le projet Sherpa')
UtilisationView = jinja_static_view('utilisation', "Mode d'emploi")
SedaView = jinja_static_view('seda', 'Le SEDA')
IndexView = jinja_static_view('index')

class SherpaReqRewriter(urlrewrite.SimpleReqRewriter):
    rules = [
        (urlrewrite.rgx('/'), dict(vid='sherpa.index')),
        (urlrewrite.rgx('/project'), dict(vid='sherpa.project')),
        (urlrewrite.rgx('/utilisation'), dict(vid='sherpa.utilisation')),
        (urlrewrite.rgx('/seda'), dict(vid='sherpa.seda')),
    ]


def registration_callback(vreg):
    from cubicweb.web.views import bookmark

    vreg.register_and_replace(IndexView, startup.IndexView)
    vreg.register_all(globals().values(), __name__, (IndexView,))
    vreg.unregister(bookmark.BookmarksBox)
