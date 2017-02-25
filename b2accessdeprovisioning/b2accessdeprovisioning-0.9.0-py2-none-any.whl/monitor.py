from __future__ import absolute_import

import json
import logging

from datetime import timedelta, datetime

import unityapiclient
from unityapiclient.client import UnityApiClient

from b2accessdeprovisioning.configparser import config
from b2accessdeprovisioning.user import User
from b2accessdeprovisioning.notifier import MailNotifier

logger = logging.getLogger(__name__)

b2access = UnityApiClient(
    config['api']['base_url'],
    auth=(config['api']['user'], config['api']['password']),
    cert_verify=config['api']['cert_verify'])

notifier = MailNotifier(
    host=config['notifications']['email']['host'],
    port=config['notifications']['email']['port'],
    use_tls=config['notifications']['email']['use_tls'],
    user=config['notifications']['email']['user'],
    password=config['notifications']['email']['password'])

def main():
    groups = b2access.get_group()
    users = []
    for member_id in groups['members']:
        entity = b2access.get_entity(member_id)
        if entity['entityInformation']['state'] != 'disabled':
            continue
        if entity['entityInformation']['scheduledOperation'] == 'REMOVE':
            continue
        user = User(internal_id=member_id)
        users.append(user)
        for identity in entity['identities']:
            if identity['typeId'] == 'persistent':
                user.shared_id = identity['value']
                break

    for user in users:
        _remove_user_attrs(user)
        _schedule_user_removal(user)
        
    if users:
        _send_notification(users)


def _remove_user_attrs(user):
    attr_whitelist = config['attr_whitelist']

    attrs = b2access.get_entity_attrs(user.internal_id, effective=False)
    for attr in attrs:
        if ('name' in attr and attr['name'] not in attr_whitelist and
            attr['visibility'] == 'full'):
            b2access.remove_entity_attr(user.internal_id, attr['name'])


def _schedule_user_removal(user):
    when = datetime.utcnow() + timedelta(days=config['retention_period'])
    b2access.schedule_operation(user.internal_id, operation='REMOVE',
                                when=when)


def _send_notification(users=[]):
    account_details = []
    for user in users:
        if user.shared_id is not None:
            account_details.append({'id': user.shared_id})
    if not account_details:
        return
    attachments = []
    attachment = {}
    attachment['filename'] = 'users.json'
    attachment['message'] = json.dumps(account_details, sort_keys=True,
                                       indent=4, separators=(',', ': '))
    attachments.append(attachment)
    notifier.send(config['notifications']['email']['from'], 
                  config['notifications']['email']['to'],
                  config['notifications']['email']['subject'], 
                  config['notifications']['email']['intro_text'],
                  attachments)


if __name__ == "__main__":
    main()
