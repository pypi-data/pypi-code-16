import argparse
import logging
import sys
import urllib.parse

import maya
import requests

from ictools import auth, cli, io


_logger = logging.getLogger(__name__)


class Connection(object):

    def __init__(self, access_token):
        self.logger = _logger.getChild('Connection')
        self.auth = auth.HTTPBearerAuth(access_token)
        self.session = requests.Session()
        response = self.session.get(
            'https://api.hipchat.com/v2/room?auth_test=true',
            auth=self.auth)
        response.raise_for_status()

    def fetch_messages(self, room, start, end):
        start = start.datetime().isoformat()
        end = end.datetime().isoformat()
        self.logger.info('fetching messages from %s between %s and %s',
                         room, start, end)
        response = self.session.get(
            'https://api.hipchat.com/v2/room/{}/history'.format(
                urllib.parse.quote(room)), auth=self.auth,
            params={'date': end, 'end-date': start})
        if response.status_code == 404:
            self.logger.error('room %s not found', room)
            return []
        response.raise_for_status()

        return _augment_messages(response.json()['items'], room)


def _augment_messages(messages, room):
    for message in messages:
        message['metadata'] = {'source': 'hipchat',
                               'date': maya.parse(message['date']),
                               'room': room}
    return messages


def scan_room():
    cli.configure_logging()
    logger = _logger.getChild('scan_room')
    api_token = cli.require_environment(logger, 'HIPCHAT_TOKEN')

    parser = argparse.ArgumentParser(
        description='Retrieve messages from HipChat',
        parents=cli.get_parent_parsers())
    parser.add_argument('--format', dest='output_format',
                        choices=('json', 'confluence'), default='json')
    parser.add_argument('start_date', metavar='START', type=maya.parse,
                        help='timestamp to start retrieving messages from')
    parser.add_argument('end_date', metavar='END', type=maya.parse,
                        help='timestamp to stop retrieving messages at')
    parser.add_argument('rooms', metavar='ROOM', nargs='+',
                        help='one or more rooms to retrieve messages from')
    args = parser.parse_args()

    conn = Connection(api_token)
    messages = []
    for room in args.rooms:
        items = conn.fetch_messages(room, args.start_date, args.end_date)
        logger.debug('found %d messages in %s', len(items), room)
        messages.extend(items)

    logger.info('found %d messages', len(messages))
    if args.output_format == 'json':
        io.dump_json(messages, sys.stdout)
    elif args.output_format == 'confluence':
        for message in messages:
            io.write_confluence_row(message['metadata']['date'],
                                    message['message'],
                                    '#' + message['metadata']['room'],
                                    sys.stdout)
