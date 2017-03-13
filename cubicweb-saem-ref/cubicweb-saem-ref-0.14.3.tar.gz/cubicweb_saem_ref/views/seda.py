# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-saem-ref views related to SEDA"""

from cubicweb.predicates import (is_instance, multi_lines_rset,
                                 has_related_entities, relation_possible)
from cubicweb.web.views import basecomponents, baseviews, ibreadcrumbs, uicfg

from cubes.seda.views.simplified import simplified_afs, simplified_pvs


# primary view configuration #######################################################################

afs = uicfg.autoform_section
afs.tag_attribute(('SEDAArchiveTransfer', 'simplified_profile'), 'main', 'hidden')

simplified_pvs.tag_attribute(('SEDAArchiveTransfer', 'ark'), 'attributes')
# we want only simplified_profile, so its default is set to true and it only has to be hidden
simplified_afs.tag_attribute(('SEDAArchiveTransfer', 'simplified_profile'), 'main', 'hidden')
# also hide transferring and archival agency
for rtype in ('seda_transferring_agency', 'seda_archival_agency'):
    # needed on afs as well as simplified_afs because it's selected during transfer creation
    afs.tag_subject_of(('SEDAArchiveTransfer', rtype, '*'), 'main', 'hidden')
    simplified_afs.tag_subject_of(('SEDAArchiveTransfer', rtype, '*'), 'main', 'hidden')
    simplified_pvs.tag_subject_of(('SEDAArchiveTransfer', rtype, '*'), 'hidden')

# copy rules from __init__ but not considered by this copy of pvs/afs
simplified_pvs.tag_subject_of(('*', 'ark_naa', '*'), 'attributes')
simplified_afs.tag_subject_of(('*', 'ark_naa', '*'), 'main', 'attributes')
simplified_afs.tag_subject_of(('*', 'custom_workflow', '*'), 'main', 'hidden')

simplified_pvs.tag_object_of(('*', 'use_profile', '*'), 'hidden')
simplified_afs.tag_object_of(('*', 'use_profile', '*'), 'main', 'hidden')

simplified_pvs.tag_attribute(('SEDABinaryDataObject', 'filename'), 'hidden')
simplified_afs.tag_attribute(('SEDABinaryDataObject', 'filename'), 'main', 'hidden')
afs.tag_attribute(('SEDABinaryDataObject', 'filename'), 'main', 'hidden')


# navigation #######################################################################################

class SEDAComponentsBreadcrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    """Breadcrumbs adapter pointing to /sedalib route when entity has no
    parent.
    """
    __select__ = (ibreadcrumbs.IBreadCrumbsAdapter.__select__
                  & relation_possible('seda_archive_unit', role='subject')
                  & ~has_related_entities('seda_archive_unit', role='subject'))

    def breadcrumbs(self, *args, **kwargs):
        return [(self._cw.build_url('sedalib'), self._cw._('SEDA components')),
                self.entity]


class SEDAComponentsBreadCrumbETypeVComponent(ibreadcrumbs.BreadCrumbEntityVComponent):
    """For proper display of the breadcrumb in the SEDA components list"""
    __select__ = (basecomponents.HeaderComponent.__select__
                  & multi_lines_rset() & is_instance('SEDAArchiveUnit'))

    def render_breadcrumbs(self, w, contextentity, path):
        w(u'<a href="%s">%s</a>' % (self._cw.build_url('sedalib'),
                                    self._cw._('SEDA components')))

# SEDA lib components ##############################################################################


class SEDALibView(baseviews.SameETypeListView):
    __regid__ = 'saem_ref.sedalib'
    __select__ = is_instance('SEDAArchiveUnit')

    @property
    def title(self):
        return self._cw._('SEDA components')
