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
"""cubicweb-sherpa components, originaly copied from the saem_ref cube."""

from cubicweb import _, tags
from cubicweb.predicates import multi_lines_rset, has_permission, is_instance
from cubicweb.web import component


def add_etype_link(req, etype, text=u'', klass='icon-plus-circled pull-right',
                   **urlparams):
    """Return an HTML link to add an entity of type 'etype'."""
    vreg = req.vreg
    eschema = vreg.schema.eschema(etype)
    if eschema.has_perm(req, 'add'):
        url = vreg['etypes'].etype_class(etype).cw_create_url(req, **urlparams)
        return tags.a(text, href=url, klass=klass,
                      title=req.__('New %s' % etype))
    return u''


def import_etype_link(req, etype, url):
    """Return an HTML link to the view that may be used to import an entity of type `etype`.
    """
    eschema = req.vreg.schema.eschema(etype)
    if eschema.has_perm(req, 'add'):
        return tags.a(u'', href=url, klass='icon-upload pull-right',
                      title=req.__('Import %s' % etype))
    return u''


class AddEntityComponent(component.CtxComponent):
    """Component with 'add' link to be displayed in 'same etype' views usually 'SameETypeListView'.
    """
    __regid__ = 'sherpa.add_entity'
    __select__ = (component.CtxComponent.__select__ & multi_lines_rset() & has_permission('add') &
                  is_instance('AuthorityRecord', 'ConceptScheme',
                              'SEDAArchiveTransfer', 'SEDAArchiveUnit'))
    context = 'navtop'
    extra_kwargs = {'SEDAArchiveUnit': {'unit_type': 'unit_content'}}

    def render_body(self, w):
        etype = self.cw_rset.description[0][0]
        w(add_etype_link(self._cw, etype, **self.extra_kwargs.get(etype, {})))


class ImportEntityComponent(component.CtxComponent):
    """Component with 'import' link to be displayed in 'same etype' views usually
    'SameETypeListView'.

    Concret class should fill the `import_vid` class attribute and add a proper `is_instance`
    selector.
    """
    __abstract__ = True
    __regid__ = 'sherpa.import_entity'
    __select__ = component.CtxComponent.__select__ & multi_lines_rset() & has_permission('add')
    import_url = None  # URL of the view that may be used to import data
    context = 'navtop'

    def render_body(self, w):
        etype = self.cw_rset.description[0][0]
        w(import_etype_link(self._cw, etype, self.import_url))


class EACImportComponent(ImportEntityComponent):
    """Component with a link to import an authority record from an EAC-CPF file."""
    __select__ = (ImportEntityComponent.__select__
                  & is_instance('AuthorityRecord'))
    _('Import AuthorityRecord')  # generate message used by the import component

    @property
    def import_url(self):
        return self._cw.build_url('view', vid='eac.import')


class SKOSImportComponent(ImportEntityComponent):
    """Component with a link to import a concept scheme from a SKOS file."""
    __select__ = ImportEntityComponent.__select__ & is_instance('ConceptScheme')
    _('Import ConceptScheme')  # generate message used by the import component

    @property
    def import_url(self):
        return self._cw.build_url('add/skossource')
