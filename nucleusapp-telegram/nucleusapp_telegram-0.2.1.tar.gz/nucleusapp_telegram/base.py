import re

import telebot
from NucleusApp.chest import Chest
from telebot.util import is_command


class TelegramBot(telebot.TeleBot):
    def __init__(self, token, threaded=True, skip_pending=False):
        super(TelegramBot, self).__init__(token, threaded, skip_pending)

    @property
    def me(self) -> telebot.types.User:
        if not hasattr(self, '_me'):
            setattr(self, '_me', self.get_me())
        return getattr(self, '_me')

    def skip_updates(self):
        """
        Get and discard all pending updates before first poll of the TelegramBot
        :return: total updates skipped
        """
        total = 0
        updates = self.get_updates(offset=self.last_update_id, timeout=1)
        while updates:
            total += len(updates)
            for update in updates:
                if update.update_id > self.last_update_id:
                    self.last_update_id = update.update_id
            updates = self.get_updates(offset=self.last_update_id + 1, timeout=1)
        return total

    def _test_filter(self, filter, filter_value, message):
        test_cases = {
            'content_types': lambda msg: msg.content_type in filter_value,
            'regexp': lambda msg: msg.content_type == 'text' and re.search(filter_value, msg.text),
            'commands': lambda msg:
            msg.content_type == 'text' and extract_command(msg.text, self.me.username) in filter_value,
            'func': lambda msg: filter_value(msg)
        }

        return test_cases.get(filter, lambda msg: False)(message)


def extract_command(text, bot_username):
    cmd = text.split()[0].split('@')
    if is_command(cmd[0]):
        if len(cmd) == 1:
            return cmd[0][1:]
        if cmd[1].lower() == bot_username.lower():
            return cmd[0][1:]
    return None


_config = Chest().root.get('settings').get('TELEGRAM')
bot = TelegramBot(token=_config['TOKEN'], skip_pending=_config.get('SKIP_PENDING', False))
