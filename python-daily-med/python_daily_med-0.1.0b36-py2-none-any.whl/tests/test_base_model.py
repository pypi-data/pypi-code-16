# -*- coding: utf-8 -*-
# Copyright 2017-TODAY LasLabs Inc.
# License MIT (https://opensource.org/licenses/MIT).

import unittest

from datetime import date

from ..models.base_model import BaseModel


class TestBaseModel(unittest.TestCase):

    def setUp(self):
        self.model = BaseModel()
        self.date_date = date(2015, 2, 1)
        self.date_str = 'Feb 01, 2015'

    def test_str_to_date(self):
        """ It should return the correct date. """
        self.assertEqual(
            self.model.str_to_date(self.date_str),
            self.date_date,
        )

    def test_date_to_str(self):
        """ It should return the correct string. """
        self.assertEqual(
            self.model.date_to_str(self.date_date),
            self.date_str,
        )
