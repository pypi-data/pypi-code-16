#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2017 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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

import csv
import json
from StringIO import StringIO

from django.conf import settings
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.test.client import Client

from ishtar_common.models import IshtarSiteProfile, ImporterModel
from ishtar_common.tests import create_superuser, TestCase

from archaeological_operations.tests import OperationInitTest, \
    ImportTest, ImportOperationTest
from archaeological_operations import models as models_ope
from archaeological_context_records import models


class ImportContextRecordTest(ImportTest, TestCase):

    fixtures = ImportOperationTest.fixtures + [
        settings.ROOT_PATH +
        '../archaeological_context_records/fixtures/initial_data-fr.json',
    ]

    def test_mcc_import_contextrecords(self):
        old_nb = models.ContextRecord.objects.count()
        mcc, form = self.init_context_record_import()

        self.assertTrue(form.is_valid())
        impt = form.save(self.ishtar_user)
        impt.initialize()

        self.init_cr_targetkey(impt)
        impt.importation()
        # new context records has now been imported
        current_nb = models.ContextRecord.objects.count()
        self.assertEqual(current_nb, old_nb + 4)
        self.assertEqual(
            models.ContextRecord.objects.filter(
                unit__txt_idx='not_in_context').count(), 3)
        self.assertEqual(
            models.ContextRecord.objects.filter(
                unit__txt_idx='layer').count(), 1)

    def test_model_limitation(self):
        old_nb = models.ContextRecord.objects.count()
        mcc, form = self.init_context_record_import()
        mcc.created_models.clear()

        self.assertTrue(form.is_valid())
        impt = form.save(self.ishtar_user)
        impt.initialize()

        self.init_cr_targetkey(impt)
        impt.importation()
        # no model defined in created_models: normal import
        current_nb = models.ContextRecord.objects.count()
        self.assertEqual(current_nb, old_nb + 4)

        # add an inadequate model to make created_models non empty
        for cr in models.ContextRecord.objects.all():
            cr.delete()
        mcc, form = self.init_context_record_import()
        mcc.created_models.clear()
        mcc.created_models.add(ImporterModel.objects.get(
            klass='ishtar_common.models.Organization'
        ))
        impt = form.save(self.ishtar_user)
        impt.initialize()
        self.init_cr_targetkey(impt)
        # Dating is not in models that can be created but force new is
        # set for a column that references Dating
        impt.importation()
        self.assertEqual(len(impt.errors), 4)
        self.assertIn("doesn't exist in the database.", impt.errors[0]['error'])

        # retry with only Dating (no context record)
        for cr in models.ContextRecord.objects.all():
            cr.delete()
        mcc, form = self.init_context_record_import()
        mcc.created_models.clear()
        dat_model, c = ImporterModel.objects.get_or_create(
            klass='archaeological_context_records.models.Dating',
            defaults={"name": 'Dating'})
        mcc.created_models.add(dat_model)
        impt = form.save(self.ishtar_user)
        impt.initialize()
        self.init_cr_targetkey(impt)
        impt.importation()

        current_nb = models.ContextRecord.objects.count()
        self.assertEqual(current_nb, 0)

        # add a context record model
        for cr in models.ContextRecord.objects.all():
            cr.delete()
        mcc, form = self.init_context_record_import()
        mcc.created_models.clear()
        mcc.created_models.add(ImporterModel.objects.get(
            klass='archaeological_context_records.models.ContextRecord'
        ))
        mcc.created_models.add(dat_model)
        impt = form.save(self.ishtar_user)
        impt.initialize()
        self.init_cr_targetkey(impt)
        impt.importation()
        current_nb = models.ContextRecord.objects.count()
        self.assertEqual(current_nb, 4)
        '''

        # add a context record model
        for cr in models.ContextRecord.objects.all():
            cr.delete()
        mcc, form = self.init_context_record_import()
        mcc.created_models.clear()
        mcc.created_models.add(ImporterModel.objects.get(
            klass='archaeological_context_records.models.ContextRecord'
        ))
        impt = form.save(self.ishtar_user)
        impt.initialize()
        self.init_cr_targetkey(impt)
        impt.importation()
        current_nb = models.ContextRecord.objects.count()
        self.assertEqual(current_nb, 4)
        '''


class ContextRecordInit(OperationInitTest):
    def create_context_record(self, user=None, data={}, force=False):
        if not getattr(self, 'context_records', None):
            self.context_records = []
        default = {'label': "Context record"}
        if force or not data.get('operation') \
                or not models.Operation.objects.filter(
                    pk=data['operation'].pk).count():
            data['operation'] = self.get_default_operation(force=force)
        if not data.get('parcel') or not data['parcel'].pk \
            or not models.Parcel.objects.filter(
                pk=data['parcel'].pk).count():
            data['parcel'] = self.get_default_parcel(force=force)
        if not data.get('history_modifier'):
            data['history_modifier'] = self.get_default_user()

        default.update(data)
        data['operation'] = models.Operation.objects.get(
            pk=data['operation'].pk)
        data['parcel'] = models.Parcel.objects.get(
            pk=data['parcel'].pk)
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


class ExportTest(ContextRecordInit, TestCase):
    fixtures = ImportContextRecordTest.fixtures

    def setUp(self):
        self.username, self.password, self.user = create_superuser()

    def test_ishtar_export_ue(self):
        ope = self.create_operation()[0]
        ope.code_patriarche = "45000"
        ope.save()
        cr = self.create_context_record(data={"label": u"CR 1"})[0]
        c = Client()
        url = reverse('get-by-importer',
                      kwargs={'slug': 'ishtar-context-record',
                              'type': 'csv'})
        response = c.get(url)
        # no result when no authentication
        self.assertTrue(not response.content)
        c.login(username=self.username, password=self.password)
        response = c.get(url)
        rows = list(csv.reader(StringIO(response.content)))
        # one header + one context record
        self.assertEqual(len(rows), 2)
        row_cr = rows[1]
        self.assertEqual(row_cr[0], '45000')
        self.assertEqual(row_cr[1], '12345')
        self.assertEqual(row_cr[2], 'A1')


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

    def test_lost_parcel_dont_delete_context_record(self):
        cr = self.create_context_record(force=True)[0]
        parcel = models.Parcel.objects.get(pk=cr.parcel.pk)
        parcel.operation = None
        parcel.save()
        # associated context record is not removed
        self.assertEqual(
            models.ContextRecord.objects.filter(pk=cr.pk).count(), 1)
        # associated operation is restored
        self.assertEqual(
            models.Parcel.objects.get(pk=parcel.pk).operation,
            cr.operation
        )

    def test_cache_update(self):
        cr = self.create_context_record()[0]
        cr_pk = cr.pk
        # OP2010 - 1 | A | 1 | CR 1
        ope_id, parcel_sec, parcel_nb, cr_label = cr.cached_label.split(' | ')
        self.assertEqual(ope_id, 'OP2010-1')
        self.assertEqual(parcel_sec, cr.parcel.section)
        self.assertEqual(parcel_nb, cr.parcel.parcel_number)
        self.assertEqual(cr_label, cr.label)

        new_lbl = "UE 2"
        cr.label = new_lbl
        cr.save()
        cr = models.ContextRecord.objects.get(pk=cr_pk)
        ope_id, parcel_sec, parcel_nb, cr_label = cr.cached_label.split(' | ')
        self.assertEqual(cr_label, new_lbl)

        new_sec, new_nb = "B", "42"
        parcel = cr.parcel
        parcel.section = new_sec
        parcel.parcel_number = new_nb
        parcel.save()
        cr = models.ContextRecord.objects.get(pk=cr_pk)
        ope_id, parcel_sec, parcel_nb, cr_label = cr.cached_label.split(' | ')
        self.assertEqual(parcel_sec, new_sec)
        self.assertEqual(parcel_nb, new_nb)

        cr.operation.year = 2017
        cr.operation.save()
        cr = models.ContextRecord.objects.get(pk=cr_pk)
        ope_id, parcel_sec, parcel_nb, cr_label = cr.cached_label.split(' | ')
        self.assertEqual(ope_id, 'OP2017-1')


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
