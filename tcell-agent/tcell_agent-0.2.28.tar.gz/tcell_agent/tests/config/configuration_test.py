# -*- coding: utf-8 -*-

from tcell_agent.config import TcellAgentConfiguration

import unittest
from ...agent import TCellAgent
import os


class TcellAgentConfigurationTest(unittest.TestCase):
    def test_setting_max_data_ex_db_records_per_request(self):
        full_path = os.path.realpath(__file__)
        data_exposure_config = os.path.join(os.path.dirname(full_path), "data_exposure.config")
        configuration = TcellAgentConfiguration(data_exposure_config)

        self.assertEqual(configuration.max_data_ex_db_records_per_request, 100)
