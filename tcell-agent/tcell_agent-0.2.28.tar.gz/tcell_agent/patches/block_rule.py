import logging

from tcell_agent.patches.sensors_matcher import SensorsMatcher

# set is builtin in python 3 but a module in earlier version
try:
    set
except NameError:
    from sets import Set as set

LOGGER = logging.getLogger('tcell_agent').getChild(__name__)


class BlockRule(object):
    ACTIONS_TO_RESPONSES = {
        "block_403s": 403
    }

    def __init__(self, ips, rids, sensors_matcher, action):
        self.ips = ips
        self.rids = rids
        self.sensors_matcher = sensors_matcher
        self.action = action

    def resp(self):
        return self.ACTIONS_TO_RESPONSES.get(self.action)

    def should_block(self, meta_data):
        if self.ips and meta_data.raw_remote_address not in self.ips:
            return False

        if self.rids and meta_data.route_id not in self.rids:
            return False

        return self.sensors_matcher.any_matches(meta_data)

    @classmethod
    def from_json(cls, rule_json):
        action = rule_json.get("action", "block_403s")

        if action in cls.ACTIONS_TO_RESPONSES:
            ips = set(rule_json.get("ips", []))
            rids = set(rule_json.get("rids", []))

            if not ips and not rids:
                LOGGER.error("Patches Policy block rule cannot be global. Specify either ips and/or route ids")

                return None

            sensors_matcher = SensorsMatcher.from_json(rule_json.get("sensor_matches", {}))

            return BlockRule(ips, rids, sensors_matcher, action)

        else:
            LOGGER.error("Patches Policy action not supported: #{action}")

            return None
