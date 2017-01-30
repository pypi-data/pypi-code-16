# copyright 2016-2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-seda unit tests for schema"""

from contextlib import contextmanager

from cubicweb import ValidationError, Unauthorized
from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.schema import ERQLExpression, RRQLExpression

import testutils


class SchemaConceptConstraintsTC(CubicWebTC):
    def setup_database(self):
        with self.admin_access.client_cnx() as cnx:
            mt_scheme = testutils.scheme_for_type(cnx, 'seda_mime_type_to', None)
            mt_concept = mt_scheme.add_concept(label=u'text/plain')
            enc_scheme = testutils.scheme_for_type(cnx, 'seda_encoding_to', None)
            enc_concept = enc_scheme.add_concept(label=u'utf-8')
            cnx.commit()
            self.mt_scheme = mt_scheme.eid
            self.mt_concept = mt_concept.eid
            self.enc_scheme = enc_scheme.eid
            self.enc_concept = enc_concept.eid

    def test_code_lists_constraints_simple(self):
        with self.admin_access.client_cnx() as cnx:
            bdo = testutils.create_transfer_to_bdo(cnx)
            bdo.container[0].cw_set(seda_reply_code_list_version=self.mt_scheme,
                                    seda_message_digest_algorithm_code_list_version=self.enc_scheme)
            cnx.commit()

            bdo.cw_set(seda_algorithm=self.mt_concept)
            with self.assertRaises(ValidationError) as cm:
                cnx.commit()
            self.assertIn('seda_algorithm-subject', cm.exception.errors)

            bdo.cw_set(seda_algorithm=self.enc_concept)
            cnx.commit()

    def assertMimeTypeConcept(self, bdo):
        cnx = bdo._cw

        cnx.create_entity('SEDAMimeType',
                          seda_mime_type_from=bdo,
                          seda_mime_type_to=self.enc_concept)
        with self.assertRaises(ValidationError) as cm:
            cnx.commit()
        self.assertIn('seda_mime_type_to-subject', cm.exception.errors)

        cnx.create_entity('SEDAMimeType',
                          seda_mime_type_from=bdo,
                          seda_mime_type_to=self.mt_concept)
        cnx.commit()

    def test_archive_transfer_mime_type_constraint(self):
        with self.admin_access.client_cnx() as cnx:
            bdo = testutils.create_transfer_to_bdo(cnx)
            cnx.commit()  # will setup code list version
            self.assertMimeTypeConcept(bdo)

    def test_component_archive_unit_mime_type_constraint(self):
        with self.admin_access.client_cnx() as cnx:
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(None, cnx=cnx)
            bdo = testutils.create_data_object(unit_alt_seq)
            cnx.commit()
            self.assertMimeTypeConcept(bdo)

    def assertEncodingConcept(self, bdo):
        cnx = bdo._cw

        cnx.create_entity('SEDAEncoding',
                          seda_encoding_from=bdo,
                          seda_encoding_to=self.mt_concept)
        with self.assertRaises(ValidationError) as cm:
            cnx.commit()
        self.assertIn('seda_encoding_to-subject', cm.exception.errors)

        cnx.create_entity('SEDAEncoding',
                          seda_encoding_from=bdo,
                          seda_encoding_to=self.enc_concept)
        cnx.commit()

    def test_archive_transfer_encoding_constraint(self):
        with self.admin_access.client_cnx() as cnx:
            bdo = testutils.create_transfer_to_bdo(cnx)
            cnx.commit()   # will setup code list version
            self.assertEncodingConcept(bdo)

    def test_component_archive_unit_encoding_constraint(self):
        with self.admin_access.client_cnx() as cnx:
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(None, cnx=cnx)
            bdo = testutils.create_data_object(unit_alt_seq)
            cnx.commit()
            self.assertEncodingConcept(bdo)

    def assertDigestAlgorithmConcept(self, bdo):
        cnx = bdo._cw

        with self.assertRaises(ValidationError) as cm:
            bdo.cw_set(seda_algorithm=self.mt_concept)
            cnx.commit()
        self.assertIn('seda_algorithm-subject', cm.exception.errors)

        bdo.cw_set(seda_algorithm=self.enc_concept)
        cnx.commit()

    def test_archive_transfer_digest_algorithm_constraint(self):
        with self.admin_access.client_cnx() as cnx:
            bdo = testutils.create_transfer_to_bdo(cnx)
            cnx.commit()  # commit first to get the container
            bdo.container[0].cw_set(seda_message_digest_algorithm_code_list_version=self.enc_scheme)
            cnx.commit()
            self.assertDigestAlgorithmConcept(bdo)

    def test_component_archive_unit_digest_algorithm_constraint(self):
        with self.admin_access.client_cnx() as cnx:
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(None, cnx=cnx)
            bdo = testutils.create_data_object(unit_alt_seq)
            bdo_type = cnx.find('CWEType', name=u'SEDABinaryDataObject').one()
            alg_type = cnx.find('CWRType', name=u'seda_algorithm').one()
            cnx.entity_from_eid(self.enc_scheme).cw_set(scheme_entity_type=bdo_type,
                                                        scheme_relation_type=alg_type)
            cnx.commit()
            self.assertDigestAlgorithmConcept(bdo)


class SchemaTC(CubicWebTC):

    def test_component_archive_unit_rule_constraint(self):
        with self.admin_access.client_cnx() as cnx:
            for rule_type in ('access', 'appraisal'):
                etype = 'SEDASeq{0}RuleRule'.format(rule_type.capitalize())
                scheme = testutils.scheme_for_type(cnx, 'seda_rule', etype)
                concept = scheme.add_concept(label=u'whatever')
                cnx.commit()

                unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(None, cnx=cnx)
                rule_rule = cnx.create_entity(etype.format(rule_type.capitalize()),
                                              seda_rule=concept)
                cnx.create_entity('SEDA{0}Rule'.format(rule_type.capitalize()),
                                  **{'seda_{0}_rule'.format(rule_type): unit_alt_seq,
                                     'seda_seq_{0}_rule_rule'.format(rule_type): rule_rule})
                cnx.commit()

    def test_rdef_container_permissions(self):
        """Check that permissions are correctly set on rdefs between entity types contained in
        SEDAArchiveTransfer."""
        for action in ('add', 'delete'):
            # Parent is container
            rdef = self.schema['seda_comment'].rdef('SEDAComment', 'SEDAArchiveTransfer')
            rqlexpr, = [p for p in rdef.permissions[action] if isinstance(p, RRQLExpression)]
            self.assertEqual(rqlexpr.expression, 'U has_update_permission O')
            # Parent is contained in container
            rdef = self.schema['seda_tag'].rdef('SEDATag',
                                                'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement')
            rqlexpr, = [p for p in rdef.permissions[action] if isinstance(p, RRQLExpression)]
            self.assertEqual(rqlexpr.expression, 'U has_update_permission C, O container C')
            # Parent is subject
            rdef = self.schema['seda_seq_alt_archive_unit_archive_unit_ref_id_management'].rdef(
                'SEDAAltArchiveUnitArchiveUnitRefId',
                'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement')
            rqlexpr, = [p for p in rdef.permissions[action] if isinstance(p, RRQLExpression)]
            self.assertEqual(rqlexpr.expression, 'U has_update_permission C, S container C')

    def test_etype_container_permissions(self):
        """Check that permissions are correctly set on entity types contained in
        SEDAArchiveTransfer."""
        for action in ('update', 'delete'):
            # Parent is container
            etype = self.schema['SEDAComment']
            rqlexpr, = [p for p in etype.permissions[action] if isinstance(p, ERQLExpression)]
            self.assertEqual(rqlexpr.expression, 'U has_{action}_permission C, '
                             'X container C'.format(action=action))

    def test_archive_unit_permissions(self):
        """Check that permissions are correctly set on archive unit that may be either container
        or contained."""
        for action in ('update', 'delete'):
            etype = self.schema['SEDAArchiveUnit']
            rqlexpr1, rqlexpr2 = [p for p in etype.permissions[action]
                                  if isinstance(p, ERQLExpression)]
            self.assertEqual(rqlexpr1.expression,
                             'U has_{action}_permission C, X container C'.format(action=action))
            self.assertEqual(rqlexpr2.expression,
                             'NOT EXISTS(X container C), U in_group G, '
                             'G name IN("managers", "users")')

    def test_rule_default_cardinality(self):
        with self.admin_access.client_cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            for rule_type in ('access', 'appraisal'):
                rule_etype = 'SEDA{0}Rule'.format(rule_type.capitalize())
                rule_rtype = 'seda_{0}_rule'.format(rule_type)
                rule = cnx.create_entity(rule_etype, **{rule_rtype: transfer})
                rule_rule_etype = 'SEDASeq{0}RuleRule'.format(rule_type.capitalize())
                rule_rule_rtype = 'reverse_seda_seq_{0}_rule_rule'.format(rule_type)
                rule_rule = cnx.create_entity(rule_rule_etype, **{rule_rule_rtype: rule})
                self.assertEqual(rule_rule.user_cardinality, '1')
                start_date = cnx.create_entity('SEDAStartDate', seda_start_date=rule_rule)
                self.assertEqual(start_date.user_cardinality, '1')

    def test_fti(self):
        # "Reverse" text to be searched in order not to be troubled by other
        # entities that may live in the DB (e.g. Concepts) with similar text.
        with self.admin_access.client_cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'Profile')
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(
                transfer, title=u'transfer name'[::-1])
            cnx.create_entity('SEDAAccessRule', seda_access_rule=unit_alt_seq,
                              user_annotation=u'some annotation'[::-1])
            testutils.create_data_object(transfer, filename=u'fixed.txt'[::-1])
            cnx.commit()

            for search in ('name', 'annotation', 'fixed'):
                with self.subTest(search=search):
                    rset = cnx.execute('Any X WHERE X has_text %(search)s',
                                       {'search': search[::-1]})
                    self.assertEqual([r for r, in rset.rows], [transfer.eid])


class SecurityTC(CubicWebTC):

    @contextmanager
    def assertUnauthorized(self, cnx):
        with self.assertRaises(Unauthorized) as cm:
            yield cm
            cnx.commit()
        cnx.rollback()

    def test_profile(self):
        with self.admin_access.repo_cnx() as cnx:
            self.create_user(cnx, login='alice')
            self.create_user(cnx, login='bob')
            cnx.commit()
        with self.new_access('alice').repo_cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'Alice Profile')
            testutils.create_archive_unit(transfer)
            testutils.create_authority_record(cnx, u'Archival inc.',
                                              reverse_seda_archival_agency=transfer)
            cnx.create_entity('SEDAComment', comment=u'Whooot.',
                              seda_comment=transfer)
            scheme = cnx.create_entity('ConceptScheme', title=u'Some vocabulary')
            cnx.create_entity('SEDAMimeTypeCodeListVersion',
                              seda_mime_type_code_list_version_from=transfer,
                              seda_mime_type_code_list_version_to=scheme)
            cnx.commit()
        with self.new_access('bob').repo_cnx() as cnx:
            transfer = cnx.entity_from_eid(transfer.eid)
            # modification of the container
            with self.assertUnauthorized(cnx):
                transfer.cw_set(title=u'Bob Profile')
            # modification of a contained entity
            comment = transfer.reverse_seda_comment[0]
            with self.assertUnauthorized(cnx):
                comment.cw_set(comment=u'You got hacked')
            with self.assertUnauthorized(cnx):
                cnx.create_entity('SEDAComment', seda_comment=transfer)
            # modification of a relation from the container to a non contained entity
            with self.assertUnauthorized(cnx):
                testutils.create_authority_record(cnx, name=u'Bob Archival inc.',
                                                  reverse_seda_archival_agency=transfer)
            # modification of a relation from a contained entity to a non contained entity
            mtclv = transfer.reverse_seda_mime_type_code_list_version_from[0]
            with self.assertUnauthorized(cnx):
                scheme = cnx.create_entity('ConceptScheme', title=u'Some nasty vocabulary')
                mtclv.cw_set(seda_mime_type_code_list_version_to=scheme)
            # deletion of a contained entity
            with self.assertUnauthorized(cnx):
                comment.cw_delete()
            # deletion of a outer relation
            with self.assertUnauthorized(cnx):
                transfer.reverse_seda_mime_type_code_list_version_from[0].cw_set(
                    seda_mime_type_code_list_version_to=None)
            # deletion of an archive unit
            with self.assertUnauthorized(cnx):
                transfer.archive_units[0].cw_delete()
            # deletion of the container
            with self.assertUnauthorized(cnx):
                transfer.cw_delete()

    def test_archive_unit(self):
        with self.admin_access.repo_cnx() as cnx:
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(None, cnx=cnx)
            cnx.commit()

            # unit has no parent, modifications are allowed.
            unit.cw_set(user_annotation=u'argh')
            unit_alt_seq.reverse_seda_title[0].cw_set(title=u'gloup')
            cnx.commit()

        with self.new_access('anon').client_cnx() as cnx:
            title = cnx.entity_from_eid(unit_alt_seq.reverse_seda_title[0].eid)
            unit = cnx.entity_from_eid(unit.eid)
            with self.assertUnauthorized(cnx):
                title.cw_set(title=u'zorglub')
            with self.assertUnauthorized(cnx):
                unit.cw_set(user_annotation=u'zorglub')
            with self.assertUnauthorized(cnx):
                cnx.create_entity('SEDADescription', seda_description=unit_alt_seq)
            with self.assertUnauthorized(cnx):
                title.cw_delete()
            with self.assertUnauthorized(cnx):
                unit.cw_delete()
        with self.admin_access.repo_cnx() as cnx:
            unit = cnx.entity_from_eid(unit.eid)
            unit.cw_delete()
            cnx.commit()


if __name__ == '__main__':
    import unittest
    unittest.main()
