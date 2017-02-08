# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

import unittest

from six import text_type

from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.web import INTERNAL_FIELD_VALUE

from cubes.seda.xsd2yams import RULE_TYPES
from cubes.seda.views import export, clone, mgmt_rules

import testutils


class ManagementRulesTC(CubicWebTC):
    def test_rule_ref_vocabulary(self):
        with self.admin_access.client_cnx() as cnx:
            create = cnx.create_entity

            access_scheme = create('ConceptScheme', title=u'access')
            access_concept = access_scheme.add_concept(label=u'anyone')
            cnx.commit()

            bdo = testutils.create_transfer_to_bdo(cnx)
            transfer = bdo.container[0]

            rule_base = create('SEDAAccessRule', seda_access_rule=transfer)
            rule_alt = create('SEDAAltAccessRulePreventInheritance',
                              reverse_seda_alt_access_rule_prevent_inheritance=rule_base)
            cnx.create_entity('SEDAPreventInheritance', seda_prevent_inheritance=rule_alt)
            cnx.commit()

            self.assertEqual(mgmt_rules._rule_ref_vocabulary(transfer, rule_base.cw_etype),
                             [('you must specify a scheme for seda_access_rule_code_list_version_'
                               'from_object to select a value', INTERNAL_FIELD_VALUE)])
            self.assertEqual(mgmt_rules._rule_ref_vocabulary(transfer, rule_alt.cw_etype),
                             [('you must specify a scheme for seda_access_rule_code_list_version_'
                               'from_object to select a value', INTERNAL_FIELD_VALUE)])

            create('SEDAAccessRuleCodeListVersion',
                   seda_access_rule_code_list_version_from=transfer,
                   seda_access_rule_code_list_version_to=access_scheme)
            cnx.commit()

            self.assertEqual(mgmt_rules._rule_ref_vocabulary(transfer, rule_base.cw_etype),
                             [('<no value specified>', '__cubicweb_internal_field__'),
                              (access_concept.label(), text_type(access_concept.eid))])
            self.assertEqual(mgmt_rules._rule_ref_vocabulary(transfer, rule_alt.cw_etype),
                             [('<no value specified>', '__cubicweb_internal_field__'),
                              (access_concept.label(), text_type(access_concept.eid))])

    def test_archive_unit_component_rule_ref_vocabulary(self):
        with self.admin_access.client_cnx() as cnx:
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(None, cnx=cnx)
            for rule_type in ('access', 'appraisal'):
                etype = 'SEDASeq{0}RuleRule'.format(rule_type.capitalize())
                scheme = testutils.scheme_for_type(cnx, 'seda_rule', etype)
                concept = scheme.add_concept(label=u'whatever')
                cnx.commit()

                unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(None, cnx=cnx)

                self.assertEqual(mgmt_rules._rule_ref_vocabulary(unit_alt_seq, etype),
                                 [('<no value specified>', '__cubicweb_internal_field__'),
                                  ('whatever', text_type(concept.eid))])


class PermissionsTC(CubicWebTC):
    """Functional test case about permissions in the web interface."""

    def test_container_permissions(self):
        """Check that a user cannot edit a SEDA profile he/she did not create."""
        alice_login = 'alice'
        bob_login = 'bob'
        with self.admin_access.repo_cnx() as cnx:
            self.create_user(cnx, login=alice_login)
            self.create_user(cnx, login=bob_login)
            cnx.commit()
        with self.new_access(alice_login).web_request() as req:
            alice_profile = req.create_entity('SEDAArchiveTransfer', title=u'Alice Profile')
            req.cnx.commit()
        with self.new_access(bob_login).web_request() as req:
            bob_profile = req.create_entity('SEDAArchiveTransfer', title=u'Bob Profile')
            req.cnx.commit()
        with self.new_access(alice_login).web_request() as req:
            alice_profile = req.entity_from_eid(alice_profile.eid)
            bob_profile = req.entity_from_eid(bob_profile.eid)
            alice_profile_form = self.vreg['forms'].select('edition', req, entity=alice_profile)
            bob_profile_form = self.vreg['forms'].select('edition', req, entity=bob_profile)
            alice_field_names = [field.name for field in alice_profile_form.fields]
            bob_field_names = [field.name for field in bob_profile_form.fields]
            for field_name in ('title',
                               'user_annotation',
                               'seda_archival_agency',
                               'seda_transferring_agency'):
                self.assertIn(field_name, alice_field_names)
                self.assertNotIn(field_name, bob_field_names)


class RelationWidgetTC(CubicWebTC):
    """Functional test case about the relation widget."""

    def test_linkable_rset(self):
        with self.admin_access.repo_cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'Test widget')
            bdo = cnx.create_entity('SEDABinaryDataObject',
                                    user_annotation=u'I am mandatory',
                                    seda_binary_data_object=transfer)
            bdo_alt = cnx.create_entity('SEDAAltBinaryDataObjectAttachment',
                                        reverse_seda_alt_binary_data_object_attachment=bdo)
            cnx.create_entity('SEDAAttachment', seda_attachment=bdo_alt)
            compressed = cnx.create_entity('SEDACompressed', seda_compressed=bdo)
            cnx.commit()
        with self.admin_access.web_request() as req:
            compressed = req.entity_from_eid(compressed.eid)
            req.form = {'relation': 'seda_algorithm:Concept:subject',
                        'container': text_type(transfer.eid)}
            view = self.vreg['views'].select('search_related_entities', req,
                                             rset=compressed.as_rset())
            self.failIf(view.linkable_rset())
        with self.admin_access.repo_cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', title=u'CompressionAlgorithm')
            scheme.add_concept(label=u'bz2')
            cnx.create_entity('SEDACompressionAlgorithmCodeListVersion',
                              seda_compression_algorithm_code_list_version_from=transfer,
                              seda_compression_algorithm_code_list_version_to=scheme)
            cnx.commit()
        with self.admin_access.web_request() as req:
            compressed = req.entity_from_eid(compressed.eid)
            req.form = {'relation': 'seda_algorithm:Concept:subject',
                        'container': text_type(transfer.eid)}
            view = self.vreg['views'].select('search_related_entities', req,
                                             rset=compressed.as_rset())
            self.assertEqual(len(view.linkable_rset()), 1)


class HelperFunctionsTC(CubicWebTC):
    def test_rtags_from_xsd_element(self):
        from cubicweb.web.views.uicfg import reledit_ctrl
        from cubes.seda.views import rtags_from_xsd_element

        rsection, display_ctrl = rtags_from_xsd_element('SEDABinaryDataObject', 'FileInfo')

        self.assertEqual(rsection.etype_get('SEDABinaryDataObject', 'filename', 'subject'),
                         None)
        self.assertEqual(reledit_ctrl.etype_get('SEDABinaryDataObject', 'filename', 'subject'),
                         {'novalue_include_rtype': False, 'novalue_label': u'<no value specified>'})


class FormatSupportedPredicateTC(CubicWebTC):

    def test_format_supported(self):
        class fakecls(object):
            def __init__(self, seda_version):
                self.seda_version = seda_version

        predicate = export.format_supported()

        with self.admin_access.web_request() as req:
            transfer = req.create_entity('SEDAArchiveTransfer', title=u'Test widget',
                                         simplified_profile=True)
            req.cnx.commit()

            for seda_version in ('2.0', '1.0', '0.2'):
                self.assertEqual(predicate(fakecls(seda_version), req, entity=transfer),
                                 1)

            self.assertEqual(predicate(fakecls(seda_version='1000'), req, entity=transfer),
                             0)

            with req.cnx.security_enabled(write=False):
                transfer.cw_set(compat_list=u'SEDA 2.0')
                req.cnx.commit()
            transfer.cw_clear_all_caches()

            self.assertEqual(predicate(fakecls(seda_version='2.0'), req, entity=transfer),
                             1)

            req.form['version'] = '2.0'  # not considered
            self.assertEqual(predicate(fakecls(seda_version='1.0'), req, entity=transfer),
                             0)

            req.form['version'] = '2.0'
            self.assertEqual(predicate(None, req, entity=transfer),
                             1)

            req.form['version'] = '1.0'
            self.assertEqual(predicate(None, req, entity=transfer),
                             0)

            del req.form['version']
            self.assertEqual(predicate(fakecls(seda_version='1.0'), req, entity=transfer,
                                       version='2.0'),
                             0)
            self.assertEqual(predicate(None, req, entity=transfer, version='2.0'),
                             1)
            self.assertEqual(predicate(None, req, entity=transfer, version='1.0'),
                             0)

            transfer.cw_set(simplified_profile=False)
            req.cnx.commit()  # will reset compat_list

            self.assertEqual(predicate(None, req, entity=transfer, version='2.0'),
                             1)
            self.assertEqual(predicate(None, req, entity=transfer, version='1.0'),
                             0)


class ArchiveTransferDiagnoseTabTC(CubicWebTC):

    def test_diagnose_tab(self):
        with self.admin_access.web_request() as req:
            transfer = req.create_entity('SEDAArchiveTransfer', title=u'diagnosis testing')
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(transfer)
            req.cnx.commit()
            # ensure the diagnosis tab display correctly
            self.view('seda_at_diagnose_tab', req=req, rset=transfer.as_rset())


class ArchiveTransferExportTC(CubicWebTC):

    def test_selected_export_class(self):
        with self.admin_access.web_request() as req:
            transfer = req.create_entity('SEDAArchiveTransfer', title=u'diagnosis testing',
                                         simplified_profile=True)
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(transfer)
            req.cnx.commit()

            exporter = self.vreg['views'].select('seda.export', req, entity=transfer)
            self.assertEqual(exporter.__class__, export.SEDAExportView)

            req.form['version'] = '0.2'
            exporter = self.vreg['views'].select('seda.export', req, entity=transfer)
            self.assertEqual(exporter.__class__, export.SEDAExportView)

            req.form['version'] = '3.0'
            exporter = self.vreg['views'].select('seda.export', req, entity=transfer)
            self.assertEqual(exporter.__class__, export.SEDANonSupportedExportView)

            with req.cnx.security_enabled(write=False):
                transfer.cw_set(compat_list=u'SEDA 2.0')
                req.cnx.commit()

            req.form['version'] = '0.2'
            exporter = self.vreg['views'].select('seda.export', req, entity=transfer)
            self.assertEqual(exporter.__class__, export.SEDANonSupportedExportView)

            req.form['version'] = '2.0'
            exporter = self.vreg['views'].select('seda.export', req, entity=transfer)
            self.assertEqual(exporter.__class__, export.SEDAExportView)


class SimplifiedFormsTC(CubicWebTC):
    """Functional test case about forms in the web interface."""

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'diagnosis testing',
                                         simplified_profile=True)
            archive_unit = testutils.create_archive_unit(transfer)[0]

            cnx.commit()
            self.transfer_eid = transfer.eid
            self.archive_unit_eid = archive_unit.eid

    def rule_form(self, req, etype, linkto=None):
        # add minimal information in for to detect container even if edited entity isn't
        # actually created
        if linkto is None:
            linkto = self.archive_unit_eid
        req.form['__linkto'] = 'x:{0}:y'.format(linkto)
        rule = req.vreg['etypes'].etype_class(etype)(req)
        return self.vreg['forms'].select('edition', req, entity=rule)

    def assertInlinedFields(self, form, expected):
        """Assert the given inlined form as the expected set of inlined forms, each defined by its
        field name and associated view class'name.
        """
        # text_type around field.name because it may be a relation schema instead of a string
        inlined_fields = [(text_type(field.name), field.view.__class__.__name__)
                          for field in form.fields if hasattr(field, 'view')]
        self.assertEqual(set(inlined_fields), set(expected))

    def assertNoRemove(self, form, field_name, role):
        """Assert the given inlined form field will be rendered without a link to remove it."""
        field = form.field_by_name(field_name, role=role)
        self.assertEqual(field.view._get_removejs(), None)

    def assertNoTitle(self, form, field_name, role):
        """Assert the given inlined form field will be rendered without form title."""
        field = form.field_by_name(field_name, role=role)
        self.assertEqual(field.view.form_renderer_id, 'notitle')

    def test_top_level_rule_form(self):
        with self.admin_access.web_request() as req:
            req.entity_from_eid(self.transfer_eid).cw_set(simplified_profile=False)
            req.cnx.commit()
            for rule_type in RULE_TYPES:
                if rule_type == 'classification':
                    continue
                with self.subTest(rule_type=rule_type):
                    form = self.rule_form(req, 'SEDA{0}Rule'.format(rule_type.capitalize()),
                                          linkto=self.transfer_eid)
                    self.assertInlinedFields(form, [
                        ('seda_seq_{0}_rule_rule'.format(rule_type),
                         'InlineAddNewLinkView'),
                    ])
            form = self.rule_form(req, 'SEDAClassificationRule'.format(rule_type.capitalize()),
                                  linkto=self.transfer_eid)
            self.assertInlinedFields(form, [
                ('seda_seq_classification_rule_rule', 'InlineAddNewLinkView'),
                ('seda_classification_reassessing_date', 'InlineAddNewLinkView'),
                ('seda_need_reassessing_authorization', 'InlineAddNewLinkView'),
            ])

    def test_top_level_rule_form_simplified(self):
        with self.admin_access.web_request() as req:
            for rule_type in ('appraisal', 'access'):
                with self.subTest(rule_type=rule_type):
                    form = self.rule_form(req, 'SEDA{0}Rule'.format(rule_type.capitalize()),
                                          linkto=self.transfer_eid)
                    self.assertInlinedFields(form, [
                        ('seda_seq_{0}_rule_rule'.format(rule_type),
                         'RuleRuleInlineEntityCreationFormView'),
                    ])

    def test_rule_form(self):
        with self.admin_access.web_request() as req:
            for rule_type in ('access', 'appraisal'):
                form = self.rule_form(req, 'SEDA{0}Rule'.format(rule_type.capitalize()))
                self.assertInlinedFields(form, [
                    ('seda_seq_{0}_rule_rule'.format(rule_type),
                     'RuleRuleInlineEntityCreationFormView'),
                    ('seda_alt_{0}_rule_prevent_inheritance'.format(rule_type),
                     'InlineAddNewLinkView'),
                ])
                self.assertNoRemove(form, 'seda_seq_{0}_rule_rule'.format(rule_type), 'subject')

    def test_rule_rule_form(self):
        with self.admin_access.web_request() as req:
            for rule_type in ('access', 'appraisal'):
                form = self.rule_form(req, 'SEDASeq{0}RuleRule'.format(rule_type.capitalize()))
                other_fields = [text_type(field.name)
                                for field in form.fields if not hasattr(field, 'view')]
                self.assertNotIn('user_cardinality', other_fields)
                self.assertInlinedFields(form, [
                    ('seda_start_date', 'StartDateInlineEntityCreationFormView'),
                ])
                self.assertNoRemove(form, 'seda_start_date', 'object')
                self.assertNoTitle(form, 'seda_start_date', 'object')

    def test_prevent_inheritance_form(self):
        with self.admin_access.web_request() as req:
            for rule_type in ('access', 'appraisal'):
                form = self.rule_form(req, 'SEDAAlt{0}RulePreventInheritance'.format(
                    rule_type.capitalize()))
                self.assertInlinedFields(form, [
                    ('seda_prevent_inheritance', 'PreventInheritanceInlineEntityCreationFormView'),
                ])
                self.assertNoRemove(form, 'seda_prevent_inheritance', 'object')
                self.assertEqual(form.form_renderer_id, 'not-an-alt')


class CloneActionsTC(CubicWebTC):

    def test_actions_notype_to_import(self):

        with self.admin_access.web_request() as req:
            transfer = req.create_entity('SEDAArchiveTransfer', title=u'test')
            unit = testutils.create_archive_unit(transfer)[0]
            req.cnx.commit()
            actions = self.pactionsdict(req, transfer.as_rset())
            self.assertIn(clone.ImportSEDAArchiveUnitAction, actions['moreactions'])
            actions = self.pactionsdict(req, unit.as_rset())
            self.assertIn(clone.ImportSEDAArchiveUnitAction, actions['moreactions'])
        with self.new_access('anon').web_request() as req:
            profile = req.entity_from_eid(transfer.eid)
            actions = self.pactionsdict(req, profile.as_rset())
            self.assertNotIn(clone.ImportSEDAArchiveUnitAction, actions['moreactions'])


class CloneImportTC(CubicWebTC):
    """Tests for 'seda.doimport' controller (called from JavaScript)."""

    def setup_database(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test')
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(None, cnx=cnx,
                                                                         user_cardinality=u'1',
                                                                         user_annotation=u'plop')
            bdo = testutils.create_data_object(unit_alt_seq, filename=u'file.txt')
            self.transfer_eid = transfer.eid
            self.unit_eid = unit.eid
            self.bdo_eid = bdo.eid
            cnx.commit()

    def doctypecode(self, cnx):
        return cnx.create_entity(
            'SEDADocumentTypeCode',
            seda_document_type_code_value=self.doctypecodevalue_eid)

    def test_import_one_entity(self):
        params = dict(eid=text_type(self.transfer_eid),
                      cloned=text_type(self.unit_eid))
        with self.admin_access.web_request(**params) as req:
            path, _ = self.expect_redirect_handle_request(
                req, 'seda.doimport')
            etype, eid = path.split('/')
            self.assertEqual(etype, 'SEDAArchiveTransfer'.lower())
            clone = req.execute('Any X WHERE X seda_archive_unit P, P eid %(p)s',
                                {'p': eid}).one()
            self.assertEqual([x.eid for x in clone.clone_of], [self.unit_eid])
            # Check that original entity attributes have been copied.
            self.assertEqual(clone.user_cardinality, u'1')
            self.assertEqual(clone.user_annotation, u'plop')
            # Check that data object has been copied and linked to the transfer
            seq = clone.first_level_choice.content_sequence
            bdo = seq.reverse_seda_data_object_reference[0].seda_data_object_reference_id[0]
            self.assertNotEqual(bdo.eid, self.bdo_eid)
            self.assertEqual(bdo.filename, 'file.txt')
            transfer = req.entity_from_eid(self.transfer_eid)
            transfer_bdos = [do.eid for do in transfer.reverse_seda_binary_data_object]
            self.assertEqual(transfer_bdos, [bdo.eid])

    def test_import_multiple_entities(self):
        with self.admin_access.cnx() as cnx:
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(
                None, cnx=cnx,
                user_cardinality=u'0..1', user_annotation=u'plouf')
            cnx.commit()
        to_clone = [self.unit_eid, unit.eid]
        params = dict(eid=text_type(self.transfer_eid),
                      cloned=','.join([text_type(self.unit_eid), text_type(unit.eid)]))
        with self.admin_access.web_request(**params) as req:
            path, _ = self.expect_redirect_handle_request(
                req, 'seda.doimport')
            etype, eid = path.split('/')
            self.assertEqual(etype, 'SEDAArchiveTransfer'.lower())
            rset = req.execute(
                'Any X,O WHERE X seda_archive_unit P, P eid %(p)s, X clone_of O',
                {'p': eid})
            self.assertEqual(len(rset), 2)
            self.assertCountEqual([oeid for __, oeid in rset.rows], to_clone)
            cardinalities, annotations = zip(*[
                (clone.user_cardinality, clone.user_annotation)
                for clone in rset.entities()])
            self.assertCountEqual(cardinalities, ('1', '0..1'))
            self.assertCountEqual(annotations, ('plop', 'plouf'))


class SEDATreeTC(CubicWebTC):

    def setup_database(self):
        with self.admin_access.cnx() as cnx:
            self.transfer_eid = cnx.create_entity('SEDAArchiveTransfer',
                                                  title=u'Test',
                                                  simplified_profile=True).eid
            cnx.commit()

    def test_archiveunit_reparent_to_transfer(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.entity_from_eid(self.transfer_eid)
            archunit, _, _ = testutils.create_archive_unit(transfer)
            transfer2 = cnx.create_entity('SEDAArchiveTransfer',
                                          title=u'Test2',
                                          simplified_profile=True)
            cnx.commit()
            archunit.cw_clear_all_caches()
            archunit.cw_adapt_to('IJQTree').reparent(transfer2.eid)
            cnx.commit()
            transfer2.cw_clear_all_caches()
            self.assertEqual([x.eid for x in transfer2.reverse_seda_archive_unit],
                             [archunit.eid])

    def test_archiveunit_reparent_to_archiveunit(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.entity_from_eid(self.transfer_eid)
            archunit, _, _ = testutils.create_archive_unit(transfer)
            archunit2, _, _ = testutils.create_archive_unit(transfer)
            cnx.commit()
            archunit.cw_clear_all_caches()
            archunit.cw_adapt_to('IJQTree').reparent(archunit2.eid)
            cnx.commit()
            seq = archunit2.first_level_choice.content_sequence
            seq.cw_clear_all_caches()
            self.assertEqual([x.eid for x in seq.reverse_seda_archive_unit],
                             [archunit.eid])

    def test_binarydataobject_reparent(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.entity_from_eid(self.transfer_eid)
            archunit, _, alt_seq = testutils.create_archive_unit(transfer)
            archunit2, _, alt_seq2 = testutils.create_archive_unit(transfer)
            bdo = testutils.create_data_object(transfer)
            ref = cnx.create_entity('SEDADataObjectReference',
                                    seda_data_object_reference=alt_seq,
                                    seda_data_object_reference_id=bdo)
            cnx.commit()
            bdo.cw_clear_all_caches()
            bdo.cw_adapt_to('IJQTree').reparent(archunit2.eid)
            cnx.commit()
            alt_seq2.cw_clear_all_caches()
            self.assertEqual([x.eid for x in alt_seq2.reverse_seda_data_object_reference],
                             [ref.eid])
            alt_seq.cw_clear_all_caches()
            self.assertFalse(alt_seq.reverse_seda_data_object_reference)


if __name__ == '__main__':
    unittest.main()
