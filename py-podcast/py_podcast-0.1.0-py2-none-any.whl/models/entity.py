import json
from datetime import datetime

class Entity(object):
  """Parent of all models of this driver"""

  def to_json(self):
    """JSON representation of the episode"""
    return json.dumps(self.__dict__, default=json_serial)

  def _build_date_str(self, d):
    """Private - builds a date, given `d`"""
    if d is not None:
      dt = datetime(d.tm_year, d.tm_mon, d.tm_mday, d.tm_hour, d.tm_min, d.tm_sec)
      return int((dt-datetime(1970,1,1)).total_seconds())
    else:
      return None
