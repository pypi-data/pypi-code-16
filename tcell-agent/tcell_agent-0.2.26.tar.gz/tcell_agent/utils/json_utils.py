import json
import logging

from tcell_agent.sanitize.sanitize_utils import ensure_str_or_unicode

LOGGER = logging.getLogger('tcell_agent').getChild(__name__)


def parse_json(encoding, json_str):
    if not json_str:
        return None

    try:
        return json.loads(ensure_str_or_unicode(encoding, json_str))
    except Exception as e:
        LOGGER.error("Error decoding json: {e}".format(e=e))
        LOGGER.debug(e, exc_info=True)
        return None
