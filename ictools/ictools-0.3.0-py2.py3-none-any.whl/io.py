import datetime
import json
import logging
import re
import sys

import bs4

from ictools import cli


TIME_FORMAT = '%b-%d %H:%M:%S'
_TIME_PATTERN = r'...-\d\d \d\d:\d\d:\d\d'


class JSONEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('indent', None)
        kwargs.setdefault('separators', (',', ':'))
        kwargs.setdefault('sort_keys', True)
        super(JSONEncoder, self).__init__(*args, **kwargs)

    def default(self, obj):
        try:
            obj = obj.datetime()
        except:
            pass

        if isinstance(obj, datetime.datetime):
            return obj.isoformat()

        return super(JSONEncoder, self).default(obj)


def dump_json(objects, stream):
    json.dump(sorted(objects, key=lambda elm: elm['metadata']['date']),
              stream, cls=JSONEncoder)


def write_confluence_row(when, message, source, stream):
    local_time = when.datetime(to_timezone='US/Eastern')
    stream.write('| {when} | {message} | {source} |\n'.format(
        when=local_time.strftime(TIME_FORMAT),
        message=html_to_confluence(message),
        source=html_to_confluence(source)))


def html_to_confluence(s):
    soup = bs4.BeautifulSoup(s, 'html.parser')
    for anchor in soup.find_all('a'):
        anchor.replace_with('[{}|{}]'.format(anchor.string, anchor['href']))
    return soup.text


def combine_tables():
    cli.configure_logging()
    logger = logging.getLogger('combine_tables')

    patn = re.compile(r'\| (?P<timestamp>' + _TIME_PATTERN + r') \|')
    lines = []
    for line in sys.stdin:
        m = patn.match(line)
        if not m:
            logger.error('failed to parse "%s"', line)
            continue
        timestamp = datetime.datetime.strptime(m.groupdict()['timestamp'],
                                               TIME_FORMAT)
        lines.append((timestamp, line))

    for _, line in sorted(lines):
        sys.stdout.write(line)
