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
"""cubicweb-saem_ref unit tests for entities.container"""

from cubicweb.devtools.testlib import CubicWebTC

from cubicweb_saem_ref.entities import container

import testutils


def sort_container(container_def):
    for k, v in container_def:
        yield k, sorted(v)


class ContainerTC(CubicWebTC):

    def test_authorityrecord_container(self):
        # line below should be copied from entities.container.registration_callback
        container_def = container.authority_record_container_def(self.schema)
        container_def = dict(sort_container(container_def))
        self.assertEqual(container_def,
                         {'Activity': [('generated', 'subject'), ('used', 'subject')],
                          'AgentFunction': [('function_agent', 'subject')],
                          'AgentPlace': [('place_agent', 'subject')],
                          'Citation': [('has_citation', 'object')],
                          'EACOtherRecordId': [('eac_other_record_id_of', 'subject')],
                          'EACResourceRelation': [('resource_relation_agent', 'subject')],
                          'EACSource': [('source_agent', 'subject')],
                          'GeneralContext': [('general_context_of', 'subject')],
                          'History': [('history_agent', 'subject')],
                          'LegalStatus': [('legal_status_agent', 'subject')],
                          'Mandate': [('mandate_agent', 'subject')],
                          'NameEntry': [('name_entry_for', 'subject')],
                          'Occupation': [('occupation_agent', 'subject')],
                          'PostalAddress': [('place_address', 'object')],
                          'Structure': [('structure_agent', 'subject')]})
        entity = self.vreg['etypes'].etype_class('AuthorityRecord')(self)
        self.assertIsNotNone(entity.cw_adapt_to('IContainer'))
        self.assertIsNone(entity.cw_adapt_to('IContained'))

    def test_scheme_container(self):
        # line below should be copied from entities.container.registration_callback
        container_def = container.scheme_container_def(self.schema)
        container_def = dict(sort_container(container_def))
        self.assertEqual(container_def,
                         {'Activity': [('generated', 'subject'), ('used', 'subject')],
                          'Concept': [('in_scheme', 'subject')]})
        entity = self.vreg['etypes'].etype_class('ConceptScheme')(self)
        self.assertIsNotNone(entity.cw_adapt_to('IContainer'))
        self.assertIsNone(entity.cw_adapt_to('IContained'))

    def test_concept_container(self):
        # line below should be copied from entities.container.registration_callback
        container_def = container.concept_container_def(self.schema)
        container_def = dict(sort_container(container_def))
        self.assertEqual(container_def,
                         {'Activity': [('generated', 'subject'), ('used', 'subject')],
                          'Label': [('label_of', 'subject')]})
        entity = self.vreg['etypes'].etype_class('Concept')(self)
        self.assertIsNotNone(entity.cw_adapt_to('IContainer'))
        # Concept is both container and contained :
        self.assertIsNotNone(entity.cw_adapt_to('IContained'))


class TreeTC(CubicWebTC):

    def test_seda_profile_clone(self):
        """Functional test for SEDA profile cloning."""
        with self.admin_access.repo_cnx() as cnx:
            scheme = testutils.setup_scheme(cnx, u'Algorithms', u'md5')
            concept = scheme.reverse_in_scheme[0]
            agent = testutils.organization_unit(cnx, u'bob', archival_roles=['deposit'])

            transfer = testutils.setup_profile(
                cnx, reverse_use_profile=agent,
                seda_message_digest_algorithm_code_list_version=scheme)

            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(
                transfer, cnx=cnx, title=u'hello')

            testutils.create_data_object(transfer, seda_algorithm=concept)

            cnx.commit()

            transfer.cw_adapt_to('IWorkflowable').fire_transition('publish')
            cnx.commit()

            clone = testutils.setup_profile(cnx, title=u'Clone', new_version_of=transfer)
            cnx.commit()

            # ark and cwuri should not have been copied
            self.assertNotEqual(clone.ark, transfer.ark)
            self.assertNotEqual(clone.cwuri, transfer.cwuri)

            # Everything else should have been copied
            self.assertEqual(clone.seda_message_digest_algorithm_code_list_version[0].eid,
                             scheme.eid)
            self.assertEqual(clone.reverse_use_profile[0].eid,
                             agent.eid)
            seq = clone.archive_units[0]. first_level_choice.content_sequence
            self.assertEqual(seq.title.title, 'hello')
            self.assertEqual(transfer.binary_data_objects[0].seda_algorithm[0].eid, concept.eid)


if __name__ == '__main__':
    import unittest
    unittest.main()
