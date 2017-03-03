# /usr/bin/env python
import time
import locale

from etherwatch.api_keys import TWILIO_KEYS
from etherwatch.api_keys import SLACK_KEYS
from etherwatch.positions import POSITIONS
from slackclient import SlackClient

locale.setlocale( locale.LC_ALL, '' )

class MessagingFunctions:
    # Writing Functions
    @staticmethod
    def write_position_message(person_str, eth_price, sign, position):
        message = '{}: ETH2USD price {}, your position is {}{} USD'.format(
            person_str,
            locale.currency(eth_price, grouping=True),
            sign,
            locale.currency(position, grouping=True)
        )
        return message

    # Rest Clients
    @staticmethod
    def get_twilio_client():
        client = TwilioRestClient(
                    TWILIO_KEYS['twilio_account_sid'],
                    TWILIO_KEYS['twilio_auth_token']
                 )
        return client

    @staticmethod
    def get_slack_client():
        client = SlackClient(SLACK_KEYS['test-token'])
        return client

    # Notifications
    @staticmethod
    def sms_notify(person_str, message):
        for person_str in POSITIONS:
            phone_number = POSITIONS[person_str]['phone_number']
            client = MessagingFunctions.get_twilio_client()
            message = client.messages.create(
                to=phone_number,
                from_=TWILIO_KEYS['twillo_numbers'][0],
                body=message
            )
            time.sleep(1)

    @staticmethod
    def slack_notify(person_str, message, channel='#positions'):
        client = MessagingFunctions.get_slack_client()
        client.api_call(
          "chat.postMessage",
          channel=channel,
          text=message
        )

    @staticmethod
    def notify(person_str, message, slack=True, sms=False):
        if slack:
            MessagingFunctions.slack_notify(person_str, message)
        if sms:
            MessagingFunctions.ms_notify(person_str, message)
