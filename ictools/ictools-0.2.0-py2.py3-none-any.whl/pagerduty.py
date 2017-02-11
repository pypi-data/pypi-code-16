import argparse
import logging
import sys

import maya
import requests
from ictools import auth, cli, io


_logger = logging.getLogger(__name__)


class Connection(object):

    def __init__(self, api_token):
        self.logger = _logger.getChild('Connection')
        self.auth = auth.HTTPTokenAuth(api_token)
        self.session = requests.Session()
        self.headers = {'Accept': 'application/vnd.pagerduty+json;version=2'}
        response = self.session.get('https://api.pagerduty.com/abilities',
                                    headers=self.headers, auth=self.auth)
        response.raise_for_status()

    def fetch_incidents_between(self, start, end):
        start = start.datetime().isoformat()
        end = end.datetime().isoformat()
        self.logger.info('fetching messages between %s and %s', start, end)

        params = {'since': start, 'until': end, 'limit': '100'}
        incidents = []

        response = self.session.get('https://api.pagerduty.com/incidents',
                                    headers=self.headers, auth=self.auth,
                                    params=params)
        response.raise_for_status()
        body = response.json()
        incidents.extend(_augment_incidents(body['incidents']))
        while body['more']:
            params['offset'] = body['offset'] + body['limit']
            response = self.session.get('https://api.pagerduty.com/incidents',
                                        headers=self.headers, auth=self.auth,
                                        params=params)
            response.raise_for_status()
            body = response.json()
            incidents.extend(_augment_incidents(body['incidents']))

        self.logger.debug('found %d incidents', len(incidents))
        return incidents


def _augment_incidents(incidents):
    for incident in incidents:
        incident['metadata'] = {'source': 'pagerduty',
                                'date': maya.parse(incident['created_at']),
                                'link': incident['self']}
    return incidents


def list_incidents():
    cli.configure_logging()
    logger = _logger.getChild('list_incidents')
    api_token = cli.require_environment(logger, 'PAGERDUTY_TOKEN')

    parser = argparse.ArgumentParser(
        description='Retrieve incidents from PagerDuty',
        parents=cli.get_parent_parsers())
    parser.add_argument('--format', dest='output_format',
                        choices=('json', 'confluence'), default='json')
    parser.add_argument('start_date', metavar='START', type=maya.parse,
                        help='earliest timestamp to retrieve incidents from')
    parser.add_argument('end_date', metavar='END', type=maya.parse,
                        help='latest timestamp to retrieve incidents from')
    args = parser.parse_args()

    conn = Connection(api_token)
    incidents = conn.fetch_incidents_between(args.start_date, args.end_date)
    logger.info('found %d messages', len(incidents))
    if args.output_format == 'json':
        io.dump_json(incidents, sys.stdout)
    elif args.output_format == 'confluence':
        for incident in incidents:
            link = '<a href="{}">PD#{}</a>'.format(
                incident['metadata']['link'], incident['incident_number'])
            io.write_confluence_row(incident['metadata']['date'],
                                    incident['description'], link, sys.stdout)
