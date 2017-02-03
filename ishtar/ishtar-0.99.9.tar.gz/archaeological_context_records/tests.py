#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# See the file COPYING for details.

import json

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from ishtar_common.models import ImporterType, IshtarSiteProfile
from ishtar_common.tests import create_superuser
from archaeological_operations.tests import OperationInitTest, \
    ImportOperationTest
from archaeological_operations import models as models_ope
from archaeological_context_records import models
from ishtar_common import forms_common


class ImportContextRecordTest(ImportOperationTest):
    test_operations = False
    test_context_records = True

    fixtures = ImportOperationTest.fixtures + [
        settings.ROOT_PATH +
        '../archaeological_context_records/fixtures/initial_data-fr.json',
    ]

    def testMCCImportContextRecords(self, test=True):
        if test and not self.test_context_records:
            return
        self.testMCCImportParcels(test=False)

        old_nb = models.ContextRecord.objects.count()
        MCC = ImporterType.objects.get(name=u"MCC - UE")
        mcc_file = open(
            settings.ROOT_PATH +
            '../archaeological_context_records/tests/'
            'MCC-context-records-example.csv', 'rb')
        file_dict = {'imported_file': SimpleUploadedFile(mcc_file.name,
                                                         mcc_file.read())}
        post_dict = {'importer_type': MCC.pk, 'skip_lines': 1,
                     "encoding": 'utf-8'}
        form = forms_common.NewImportForm(data=post_dict, files=file_dict,
                                          instance=None)
        form.is_valid()
        if test:
            self.assertTrue(form.is_valid())
        impt = form.save(self.ishtar_user)
        impt.initialize()

        # doing manual connections
        hc = models.Unit.objects.get(txt_idx='not_in_context').pk
        self.setTargetKey('unit', 'hc', hc)
        self.setTargetKey('unit', 'hors-contexte', hc)
        layer = models.Unit.objects.get(txt_idx='layer').pk
        self.setTargetKey('unit', 'couche', layer)

        impt.importation()
        if not test:
            return

        # new ues has now been imported
        current_nb = models.ContextRecord.objects.count()
        self.assertTrue(current_nb == (old_nb + 4))
        self.assertEqual(
            models.ContextRecord.objects.filter(unit__pk=hc).count(), 3)
        self.assertEqual(
            models.ContextRecord.objects.filter(unit__pk=layer).count(), 1)


class ContextRecordInit(OperationInitTest):
    test_operations = False

    def create_context_record(self, user=None, data={}, force=False):
        if not getattr(self, 'context_records', None):
            self.context_records = []

        default = {'label': "Context record"}
        if force or not data.get('operation'):
            data['operation'] = self.get_default_operation(force=force)
        if not data.get('parcel') or not data['parcel'].pk:
            data['parcel'] = self.get_default_parcel(force=force)
        if not data.get('history_modifier'):
            data['history_modifier'] = self.get_default_user()

        default.update(data)
        self.context_records.append(models.ContextRecord.objects.create(
            **default))
        return self.context_records

    def get_default_context_record(self, force=False):
        if force:
            return self.create_context_record(force=force)[-1]
        return self.create_context_record(force=force)[0]

    def tearDown(self):
        if hasattr(self, 'context_records'):
            for cr in self.context_records:
                try:
                    cr.delete()
                except:
                    pass
            self.context_records = []
        super(ContextRecordInit, self).tearDown()


class ContextRecordTest(ContextRecordInit, TestCase):
    fixtures = ImportContextRecordTest.fixtures

    def setUp(self):
        IshtarSiteProfile.objects.create()
        self.username, self.password, self.user = create_superuser()
        self.create_context_record(data={"label": u"CR 1"})
        self.create_context_record(data={"label": u"CR 2"})

        cr_1 = self.context_records[0]
        cr_2 = self.context_records[1]
        sym_rel_type = models.RelationType.objects.filter(
            symmetrical=True).all()[0]
        self.cr_rel_type = sym_rel_type
        models.RecordRelations.objects.create(
            left_record=cr_1, right_record=cr_2, relation_type=sym_rel_type)

    def testExternalID(self):
        cr = self.context_records[0]
        self.assertEqual(
            cr.external_id,
            u"{}-{}".format(cr.parcel.external_id, cr.label))


class ContextRecordSearchTest(ContextRecordInit, TestCase):
    fixtures = ImportContextRecordTest.fixtures

    def setUp(self):
        IshtarSiteProfile.objects.create()
        self.username, self.password, self.user = create_superuser()
        self.create_context_record(data={"label": u"CR 1"})
        self.create_context_record(data={"label": u"CR 2"})

        cr_1 = self.context_records[0]
        cr_2 = self.context_records[1]
        sym_rel_type = models.RelationType.objects.filter(
            symmetrical=True).all()[0]
        self.cr_rel_type = sym_rel_type
        models.RecordRelations.objects.create(
            left_record=cr_1, right_record=cr_2, relation_type=sym_rel_type)

    def testSearchExport(self):
        c = Client()
        response = c.get(reverse('get-contextrecord'))
        # no result when no authentification
        self.assertTrue(not json.loads(response.content))
        c.login(username=self.username, password=self.password)
        response = c.get(reverse('get-contextrecord'))
        self.assertTrue(json.loads(response.content)['total'] == 2)
        # test search label
        response = c.get(reverse('get-contextrecord'),
                         {'label': 'cr 1'})
        self.assertEqual(json.loads(response.content)['total'], 1)
        # test search between relations
        response = c.get(reverse('get-contextrecord'),
                         {'label': 'cr 1',
                          'relation_types_0': self.cr_rel_type.pk})
        self.assertEqual(json.loads(response.content)['total'], 2)
        # test search between related operations
        first_ope = self.operations[0]
        first_ope.year = 2010
        first_ope.save()
        cr_1 = self.context_records[0]
        cr_1.operation = first_ope
        cr_1.save()
        other_ope = self.operations[1]
        other_ope.year = 2016
        other_ope.save()
        cr_2 = self.context_records[1]
        cr_2.operation = other_ope
        cr_2.save()
        rel_ope = models_ope.RelationType.objects.create(
            symmetrical=True, label='Linked', txt_idx='link')
        models_ope.RecordRelations.objects.create(
            left_record=other_ope,
            right_record=first_ope,
            relation_type=rel_ope)
        response = c.get(reverse('get-contextrecord'),
                         {'operation__year': 2010,
                          'ope_relation_types_0': rel_ope.pk})
        self.assertEqual(json.loads(response.content)['total'], 2)
        # export
        response = c.get(reverse('get-contextrecord-full',
                                 kwargs={'type': 'csv'}), {'submited': '1'})
        # 2 lines + header
        lines = [line for line in response.content.split('\n') if line]
        self.assertEqual(len(lines), 3)

    def testUnitHierarchicSearch(self):
        cr = self.context_records[0]
        c = Client()

        neg = models.Unit.objects.get(txt_idx='negative')
        dig = models.Unit.objects.get(txt_idx='digging')
        dest = models.Unit.objects.get(txt_idx='partial_destruction')
        cr.unit = (dig)
        cr.save()
        search = {'unit': dig.pk}

        # no result when no authentication
        response = c.get(reverse('get-contextrecord'), search)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(not json.loads(response.content))

        # one result for exact search
        c.login(username=self.username, password=self.password)
        response = c.get(reverse('get-contextrecord'), search)
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertTrue(res['total'] == 1)
        self.assertEqual(res["rows"][0]["unit"],
                         unicode(dig))

        # no result for the brother
        search = {'unit': dest.pk}
        response = c.get(reverse('get-contextrecord'), search)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['total'], 0)

        # one result for the father
        search = {'unit': neg.pk}
        response = c.get(reverse('get-contextrecord'), search)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['total'], 1)

    def testPeriodHierarchicSearch(self):
        cr = self.context_records[0]
        c = Client()

        neo = models.Period.objects.get(txt_idx='neolithic')
        final_neo = models.Period.objects.get(txt_idx='final_neolithic')
        recent_neo = models.Period.objects.get(txt_idx='recent_neolithic')
        dating = models.Dating.objects.create(
            period=final_neo
        )
        cr.datings.add(dating)

        search = {'datings__period': final_neo.pk}

        # no result when no authentication
        response = c.get(reverse('get-contextrecord'), search)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(not json.loads(response.content))

        # one result for exact search
        c.login(username=self.username, password=self.password)
        response = c.get(reverse('get-contextrecord'), search)
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.content)
        self.assertTrue(res['total'] == 1)

        # no result for the brother
        search = {'datings__period': recent_neo.pk}
        response = c.get(reverse('get-contextrecord'), search)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['total'], 0)

        # one result for the father
        search = {'datings__period': neo.pk}
        response = c.get(reverse('get-contextrecord'), search)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['total'], 1)


class RecordRelationsTest(ContextRecordInit, TestCase):
    fixtures = ImportOperationTest.fixtures
    model = models.ContextRecord

    def setUp(self):
        # two different context records
        self.create_context_record({"label": u"CR 1"})
        self.create_context_record({"label": u"CR 2"})

    def testRelations(self):
        sym_rel_type = models.RelationType.objects.create(
            symmetrical=True, txt_idx='sym')
        rel_type_1 = models.RelationType.objects.create(
            symmetrical=False, txt_idx='rel_1')
        # cannot be symmetrical and have an inverse_relation
        with self.assertRaises(ValidationError):
            rel_test = models.RelationType.objects.create(
                symmetrical=True, inverse_relation=rel_type_1, txt_idx='rel_3')
            rel_test.full_clean()
        # auto fill inverse relations
        rel_type_2 = models.RelationType.objects.create(
            symmetrical=False, inverse_relation=rel_type_1, txt_idx='rel_2')
        self.assertEqual(rel_type_1.inverse_relation, rel_type_2)

        cr_1 = self.context_records[0]
        cr_2 = self.context_records[1]

        # inserting a new symmetrical relation automatically creates the same
        # relation for the second context record
        rel = models.RecordRelations.objects.create(
            left_record=cr_1, right_record=cr_2, relation_type=sym_rel_type)
        self.assertEqual(models.RecordRelations.objects.filter(
            left_record=cr_2, right_record=cr_1,
            relation_type=sym_rel_type).count(), 1)

        # removing one symmetrical relation removes the other
        rel.delete()
        self.assertEqual(models.RecordRelations.objects.filter(
            left_record=cr_2, right_record=cr_1,
            relation_type=sym_rel_type).count(), 0)

        # for non-symmetrical relation, adding one relation automatically
        # adds the inverse
        rel = models.RecordRelations.objects.create(
            left_record=cr_1, right_record=cr_2, relation_type=rel_type_1)
        self.assertEqual(models.RecordRelations.objects.filter(
            left_record=cr_2, right_record=cr_1,
            relation_type=rel_type_2).count(), 1)
