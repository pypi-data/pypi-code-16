import requests
import pandas as pd
import json
import datetime
from requests.packages.urllib3.exceptions import SubjectAltNameWarning
import warnings
import logging
warnings.simplefilter('ignore', SubjectAltNameWarning)

logger = logging.getLogger(__name__)

MIN_DATE = datetime.datetime.fromtimestamp(0).isoformat()
MAX_DATE = datetime.datetime.today() + datetime.timedelta(days=365)


def _default(value):
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.isoformat()
    try:
        return float(value)
    except:
        pass


class Client(object):
    def __init__(self, url, **kwargs):
        self._url = url.rstrip('/')
        self.s = requests.Session()

    def _process_errors(self, res):
        if res.status_code != 200:
            raise Exception(res.json())
        return True

    def _build_url(self, part):
        return '/'.join((self._url, part.lstrip('/')))

    def list(self):
        url = self._build_url('/table')
        res = self.s.get(url)
        return res.json()

    def exists(self, table):
        url = self._build_url('/table/{}'.format(table))
        return self.s.get(url).status_code == 200

    def delete(self, table):
        if self.exists(table):
            url = self._build_url('/table/{}'.format(table))
            return self.s.delete(url).status_code == 200
        else:
            logger.warning('table {} does not exist'.format(table))
        return True

    def create(self, table):
        if not self.exists(table):
            url = self._build_url('/table/{}'.format(table))
            res = self.s.post(
                url, data={'created-with': 'tourbillon python client'})
            return self._process_errors(res)
        else:
            logger.warning('table {} already exists'.format(table))
        return True

    def read(self, table, start=MIN_DATE, end=MAX_DATE, create=False,
             **kwargs):
        if not self.exists(table) and create:
            self.create(table)
        url = self._build_url('/table/{}/data'.format(table))
        params = kwargs
        params.update({'start': start, 'end': end})
        res = self.s.get(url, params=params)
        if self._process_errors(res):
            df = pd.read_json(res.text)
            df.index = pd.to_datetime(df['index'])
            del df['index']
            return df

    def write(self, table, data):
        url = self._build_url('/table/{}/data'.format(table))
        records = [(timestamp, value)
                   for timestamp, value in data.to_records()]
        payload = json.dumps(records, default=_default)
        res = self.s.post(
            url, data=payload, headers={'Content-Type': 'application/json'})
        return self._process_errors(res)
