from couchbase.bucket import Bucket
from storer import Storer
import threading
import datetime
import sys
import os

class CouchbaseStorer(Storer):
  """Storer of podcasts in Couchbase"""

  def __init__(self, url, password=None):
    """Constructor"""
    self.url      = url # Bucket URL
    self.password = password # Bucket password
    self.lock     = threading.Lock() # Thread-safe utilization of this driver
    self.db       = Bucket(self.url) if self.password is None else Bucket(self.url, password=self.password)

  def _make_series_key(self, series_dict):
    """Series key for Couchbase"""
    return str(series_dict['id']) + ':' + str(sys.maxsize)


  def _make_episode_key(self, series_id, episode_dict):
    """Episode key for Couchbase"""
    return str(series_id) + ':' + str(episode_dict['pubDate'])


  def store(self, result_dict):
    """See Storer#store(result_json)"""
    # Build properly formatted bulk insert
    bulk_upsert = dict()
    series_id = result_dict['series']['id']
    bulk_upsert[self._make_series_key(result_dict['series'])] = result_dict['series']
    for e in result_dict['episodes']:
      bulk_upsert[self._make_episode_key(series_id, e)] = e

    # Bulk insert (thread-safe)
    self.lock.acquire()
    self.db.upsert_multi(bulk_upsert)
    self.lock.release()
