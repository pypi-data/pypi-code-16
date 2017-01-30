#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests del modulo pydatajson."""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import with_statement

import os.path
import unittest
import json
import nose
import vcr
from collections import OrderedDict
import filecmp
from .context import pydatajson
from . import xl_methods
import openpyxl as pyxl

my_vcr = vcr.VCR(path_transformer=vcr.VCR.ensure_suffix('.yaml'),
                 cassette_library_dir=os.path.join("tests", "cassetes"),
                 record_mode='once')


class ReadersAndWritersTestCase(unittest.TestCase):

    SAMPLES_DIR = os.path.join("tests", "samples")
    RESULTS_DIR = os.path.join("tests", "results")
    TEMP_DIR = os.path.join("tests", "temp")

    @classmethod
    def get_sample(cls, sample_filename):
        return os.path.join(cls.SAMPLES_DIR, sample_filename)

    @classmethod
    def setUp(cls):
        cls.dj = pydatajson.DataJson()
        cls.maxDiff = None
        cls.longMessage = True

    @classmethod
    def tearDown(cls):
        del(cls.dj)

    # TESTS DE READ_TABLE y WRITE_TABLE

    CSV_TABLE = [
        OrderedDict([(u'Plato', u'Milanesa'),
                     (u'Precio', u'Bajo'),
                     (u'Sabor', u'666')]),
        OrderedDict([(u'Plato', u'Thoné, Vitel'),
                     (u'Precio', u'Alto'),
                     (u'Sabor', u'8000')]),
        OrderedDict([(u'Plato', u'Aceitunas'),
                     (u'Precio', u''),
                     (u'Sabor', u'15')])
    ]

    WRITE_XLSX_TABLE = [
        OrderedDict([(u'Plato', u'Milanesa'),
                     (u'Precio', u'Bajo'),
                     (u'Sabor', 666)]),
        OrderedDict([(u'Plato', u'Thoné, Vitel'),
                     (u'Precio', u'Alto'),
                     (u'Sabor', 8000)]),
        OrderedDict([(u'Plato', u'Aceitunas'),
                     (u'Precio', None),
                     (u'Sabor', 15)])
    ]

    READ_XLSX_TABLE = [
        OrderedDict([(u'Plato', u'Milanesa'),
                     (u'Precio', u'Bajo'),
                     (u'Sabor', 666)]),
        OrderedDict([(u'Plato', u'Thoné, Vitel'),
                     (u'Precio', u'Alto'),
                     (u'Sabor', 8000)]),
        OrderedDict([(u'Plato', u'Aceitunas'),
                     (u'Sabor', 15)])
    ]

    def test_read_table_from_csv(self):
        csv_filename = os.path.join(self.SAMPLES_DIR, "read_table.csv")
        actual_table = pydatajson.readers.read_table(csv_filename)
        expected_table = self.CSV_TABLE

        for (actual_row, expected_row) in zip(actual_table, expected_table):
            self.assertEqual(actual_row, expected_row)

    def test_read_table_from_xlsx(self):
        xlsx_filename = os.path.join(self.SAMPLES_DIR, "read_table.xlsx")
        actual_table = pydatajson.readers.read_table(xlsx_filename)
        expected_table = self.READ_XLSX_TABLE

        for (actual_row, expected_row) in zip(actual_table, expected_table):
            self.assertEqual(dict(actual_row), dict(expected_row))

        self.assertListEqual(actual_table, expected_table)

    def test_write_table_to_csv(self):
        expected_filename = os.path.join(self.RESULTS_DIR, "write_table.csv")
        actual_filename = os.path.join(self.TEMP_DIR, "write_table.csv")

        pydatajson.writers.write_table(self.CSV_TABLE, actual_filename)
        comparison = filecmp.cmp(actual_filename, expected_filename)
        if comparison:
            os.remove(actual_filename)
        else:
            """
{} se escribió correctamente, pero no es idéntico al esperado. Por favor,
revíselo manualmente""".format(actual_filename)

        self.assertTrue(comparison)

    def test_write_table_to_xlsx(self):
        expected_filename = os.path.join(self.RESULTS_DIR, "write_table.xlsx")
        actual_filename = os.path.join(self.TEMP_DIR, "write_table.xlsx")

        pydatajson.writers.write_table(self.WRITE_XLSX_TABLE, actual_filename)
        expected_wb = pyxl.load_workbook(expected_filename)
        actual_wb = pyxl.load_workbook(actual_filename)

        self.assertTrue(xl_methods.compare_cells(actual_wb, expected_wb))

        os.remove(actual_filename)

    def test_write_read_csv_loop(self):
        """Escribir y leer un CSV es una operacion idempotente."""
        temp_filename = os.path.join(self.TEMP_DIR, "write_read_loop.csv")
        pydatajson.writers.write_table(self.CSV_TABLE, temp_filename)
        read_table = pydatajson.readers.read_table(temp_filename)

        comparison = (self.CSV_TABLE == read_table)
        if comparison:
            os.remove(temp_filename)
        else:
            """
{} se escribió correctamente, pero no es idéntico al esperado. Por favor,
revíselo manualmente""".format(temp_filename)

        self.assertListEqual(read_table, self.CSV_TABLE)

    def test_write_read_xlsx_loop(self):
        """Escribir y leer un XLSX es una operacion idempotente."""
        temp_filename = os.path.join(self.TEMP_DIR, "write_read_loop.xlsx")
        pydatajson.writers.write_table(self.WRITE_XLSX_TABLE, temp_filename)
        read_table = pydatajson.readers.read_table(temp_filename)

        # read_xlsx_table no lee celdasd nulas. Por lo tanto, si hay una clave
        # de valor None en la tabla original, al leerla y escribirla dicha
        # clave no estará presente. Por eso se usa d.get(k) en lugar de d[k].
        for (actual_row, expected_row) in zip(read_table,
                                              self.WRITE_XLSX_TABLE):
            for key in expected_row.keys():
                self.assertEqual(actual_row.get(key), expected_row.get(key))

        os.remove(temp_filename)

    def test_read_local_xlsx_catalog(self):
        workbook_path = os.path.join(self.SAMPLES_DIR,
                                     "catalogo_justicia.xlsx")
        actual_dict = pydatajson.readers.read_local_xlsx_catalog(workbook_path)

        result_path = os.path.join(self.RESULTS_DIR, "catalogo_justicia.json")
        with open(result_path) as result_file:
            expected_dict = json.load(result_file, encoding='utf-8')

        self.assertDictEqual(actual_dict, expected_dict)


if __name__ == '__main__':
    nose.run(defaultTest=__name__)
