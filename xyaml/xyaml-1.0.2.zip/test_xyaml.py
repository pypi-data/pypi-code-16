#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from unittest import TestCase

import xyaml

__author__ = 'Marco Bartel'


class TestXyaml(TestCase):
    def test_load(self):
        config = xyaml.load(r"examples/config.yaml")
        print(json.dumps(config, sort_keys=True, indent=4))
