import unittest

from tcell_agent.config import CONFIGURATION
from tcell_agent.agent.metrics import AgentMetrics


class AgentMetricsAddSessionTrackMetricTest(unittest.TestCase):
    def setUp(self):
        self.orig_hipaa_safe_mode = CONFIGURATION.hipaa_safe_mode
        self.orig_hmac_key = CONFIGURATION.hmac_key

    def tearDown(self):
        CONFIGURATION.hipaa_safe_mode = self.orig_hipaa_safe_mode
        CONFIGURATION.hmac_key = self.orig_hmac_key

    def add_session_track_metric_test_hipaa_enabled_tests(self):
        CONFIGURATION.hipaa_safe_mode = True
        CONFIGURATION.hmac_key = "secret_hmac_key"

        agent_metrics = AgentMetrics()
        agent_metrics.add_session_track_metric("hmacd_session_id", "tcelluser@tcell.io", "user_agent", "ip")

        self.assertEqual(len(agent_metrics._session_metrics["hmacd_session_id"]), 1)
        self.assertEqual(
            agent_metrics._session_metrics["hmacd_session_id"][0]["uid"],
            "7a5c99b249e48fa7bbd3263029ecc907b24619b4d81361606b19f2696f50e43a")

    def add_session_track_metric_test_hipaa_disabled_tests(self):
        CONFIGURATION.hipaa_safe_mode = False
        CONFIGURATION.hmac_key = "secret_hmac_key"

        agent_metrics = AgentMetrics()
        agent_metrics.add_session_track_metric("hmacd_session_id", "tcelluser@tcell.io", "user_agent", "ip")

        self.assertEqual(len(agent_metrics._session_metrics["hmacd_session_id"]), 1)
        self.assertEqual(
            agent_metrics._session_metrics["hmacd_session_id"][0]["uid"],
            "tcelluser@tcell.io")
