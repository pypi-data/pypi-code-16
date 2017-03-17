import unittest

from tcell_agent.appsensor.sensors.payloads_policy import PayloadsPolicy

# set is builtin in python 3 but a module in earlier version
try:
    set
except NameError:
    from sets import Set as set


class PayloadsPolicyTest(unittest.TestCase):
    def from_json_none_options_test(self):
        policy_json = None
        policy = PayloadsPolicy.from_json(policy_json)

        self.assertFalse(policy.send_payloads)
        self.assertFalse(policy.log_payloads)
        self.assertEqual(policy.send_blacklist, policy.DEFAULT_BLACKLIST)
        self.assertEqual(policy.send_whitelist, {})
        self.assertFalse(policy.use_send_whitelist)
        self.assertEqual(policy.log_blacklist, policy.DEFAULT_BLACKLIST)
        self.assertEqual(policy.log_whitelist, {})
        self.assertFalse(policy.use_log_whitelist)

    def from_json_none_payloads_test(self):
        policy_json = {}
        policy = PayloadsPolicy.from_json(policy_json)

        self.assertFalse(policy.send_payloads)
        self.assertFalse(policy.log_payloads)
        self.assertEqual(policy.send_blacklist, policy.DEFAULT_BLACKLIST)
        self.assertEqual(policy.send_whitelist, {})
        self.assertFalse(policy.use_send_whitelist)
        self.assertEqual(policy.log_blacklist, policy.DEFAULT_BLACKLIST)
        self.assertEqual(policy.log_whitelist, {})
        self.assertFalse(policy.use_log_whitelist)

    def from_json_empty_payloads_test(self):
        policy_json = {"payloads": {}}
        policy = PayloadsPolicy.from_json(policy_json)

        self.assertFalse(policy.send_payloads)
        self.assertFalse(policy.log_payloads)
        self.assertEqual(policy.send_blacklist, policy.DEFAULT_BLACKLIST)
        self.assertEqual(policy.send_whitelist, {})
        self.assertFalse(policy.use_send_whitelist)
        self.assertEqual(policy.log_blacklist, policy.DEFAULT_BLACKLIST)
        self.assertEqual(policy.log_whitelist, {})
        self.assertFalse(policy.use_log_whitelist)

    def from_json_payloads_false_send_payloads_test(self):
        policy_json = {"payloads": {"send_payloads": False}}
        policy = PayloadsPolicy.from_json(policy_json)

        self.assertFalse(policy.send_payloads)
        self.assertFalse(policy.log_payloads)
        self.assertEqual(policy.send_blacklist, policy.DEFAULT_BLACKLIST)
        self.assertEqual(policy.send_whitelist, {})
        self.assertFalse(policy.use_send_whitelist)
        self.assertEqual(policy.log_blacklist, policy.DEFAULT_BLACKLIST)
        self.assertEqual(policy.log_whitelist, {})
        self.assertFalse(policy.use_log_whitelist)

    def from_json_payloads_false_send_payloads_with_send_blacklist_send_whitelist_test(self):
        policy_json = {
            "payloads": {
                "send_payloads": False,
                "send_blacklist": {
                    "username": ["*"]
                },
                "send_whitelist": {
                    "password": ["*"]
                }
            }
        }
        policy = PayloadsPolicy.from_json(policy_json)

        self.assertFalse(policy.send_payloads)
        self.assertFalse(policy.log_payloads)
        self.assertEqual(policy.send_blacklist, policy.DEFAULT_BLACKLIST)
        self.assertEqual(policy.send_whitelist, {})
        self.assertFalse(policy.use_send_whitelist)
        self.assertEqual(policy.log_blacklist, policy.DEFAULT_BLACKLIST)
        self.assertEqual(policy.log_whitelist, {})
        self.assertFalse(policy.use_log_whitelist)

    def from_json_payloads_true_send_payloads_test(self):
        policy_json = {"payloads": {"send_payloads": True}}
        policy = PayloadsPolicy.from_json(policy_json)

        self.assertTrue(policy.send_payloads)
        self.assertFalse(policy.log_payloads)
        self.assertEqual(policy.send_blacklist, policy.DEFAULT_BLACKLIST)
        self.assertEqual(policy.send_whitelist, {})
        self.assertFalse(policy.use_send_whitelist)
        self.assertEqual(policy.log_blacklist, policy.DEFAULT_BLACKLIST)
        self.assertEqual(policy.log_whitelist, {})
        self.assertFalse(policy.use_log_whitelist)

    def from_json_payloads_true_send_payloads_with_send_blacklist_send_whitelist_test(self):
        policy_json = {
            "payloads": {
                "send_payloads": True,
                "send_blacklist": {
                    "username": ["*"],
                    "password": ["form"]
                },
                "send_whitelist": {
                    "password": ["*"]
                }
            }
        }
        policy = PayloadsPolicy.from_json(policy_json)

        self.assertTrue(policy.send_payloads)
        self.assertFalse(policy.log_payloads)
        self.assertEqual(policy.send_blacklist, {"username": set(["*"]), "password": set(["form"])})
        self.assertEqual(policy.send_whitelist, {"password": set(["*"])})
        self.assertTrue(policy.use_send_whitelist)
        self.assertEqual(policy.log_blacklist, policy.DEFAULT_BLACKLIST)
        self.assertEqual(policy.log_whitelist, {})
        self.assertFalse(policy.use_log_whitelist)

    def from_json_payloads_false_log_payloads_test(self):
        policy_json = {"payloads": {"log_payloads": False}}
        policy = PayloadsPolicy.from_json(policy_json)

        self.assertFalse(policy.send_payloads)
        self.assertFalse(policy.log_payloads)
        self.assertEqual(policy.send_blacklist, policy.DEFAULT_BLACKLIST)
        self.assertEqual(policy.send_whitelist, {})
        self.assertFalse(policy.use_send_whitelist)
        self.assertEqual(policy.log_blacklist, policy.DEFAULT_BLACKLIST)
        self.assertEqual(policy.log_whitelist, {})
        self.assertFalse(policy.use_log_whitelist)

    def from_json_payloads_false_log_payloads_with_log_blacklist_log_whitelist_test(self):
        policy_json = {
            "payloads": {
                "log_payloads": False,
                "log_blacklist": {
                    "username": ["*"]
                },
                "log_whitelist": {
                    "password": ["*"]
                }
            }
        }
        policy = PayloadsPolicy.from_json(policy_json)

        self.assertFalse(policy.send_payloads)
        self.assertFalse(policy.log_payloads)
        self.assertEqual(policy.send_blacklist, policy.DEFAULT_BLACKLIST)
        self.assertEqual(policy.send_whitelist, {})
        self.assertFalse(policy.use_send_whitelist)
        self.assertEqual(policy.log_blacklist, policy.DEFAULT_BLACKLIST)
        self.assertEqual(policy.log_whitelist, {})
        self.assertFalse(policy.use_log_whitelist)

    def from_json_payloads_true_log_payloads_test(self):
        policy_json = {"payloads": {"log_payloads": True}}
        policy = PayloadsPolicy.from_json(policy_json)

        self.assertFalse(policy.send_payloads)
        self.assertTrue(policy.log_payloads)
        self.assertEqual(policy.send_blacklist, policy.DEFAULT_BLACKLIST)
        self.assertEqual(policy.send_whitelist, {})
        self.assertFalse(policy.use_send_whitelist)
        self.assertEqual(policy.log_blacklist, policy.DEFAULT_BLACKLIST)
        self.assertEqual(policy.log_whitelist, {})
        self.assertFalse(policy.use_log_whitelist)

    def from_json_payloads_true_log_payloads_with_log_blacklist_log_whitelist_test(self):
        policy_json = {
            "payloads": {
                "log_payloads": True,
                "log_blacklist": {
                    "username": ["*"],
                    "password": ["form"]
                },
                "log_whitelist": {
                    "password": ["*"]
                }
            }
        }
        policy = PayloadsPolicy.from_json(policy_json)

        self.assertFalse(policy.send_payloads)
        self.assertTrue(policy.log_payloads)
        self.assertEqual(policy.send_blacklist, policy.DEFAULT_BLACKLIST)
        self.assertEqual(policy.send_whitelist, {})
        self.assertFalse(policy.use_send_whitelist)
        self.assertEqual(policy.log_blacklist, {"username": set(["*"]), "password": set(["form"])})
        self.assertEqual(policy.log_whitelist, {"password": set(["*"])})
        self.assertTrue(policy.use_log_whitelist)
