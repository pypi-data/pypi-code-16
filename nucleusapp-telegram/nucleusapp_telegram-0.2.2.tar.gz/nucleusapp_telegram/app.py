import logging

import telebot
from NucleusApp.chest import Chest
from NucleusApp.modules.config import AppConfig
from TeleSocketClient import TeleSocket as TeleSocket
from TeleSocketClient.manager import TeleSocket as TeleSocketManager

from .base import bot
from .utils import BOT_CHEST_ENTITY

log = logging.getLogger('TeleBot')


class Config(AppConfig):
    def ready(self):
        self.config = self.application.settings.get('TELEGRAM')
        self.bot = bot
        self.telesocket = TeleSocketManager() if self.config.get('TELESOCKET_MANAGER', False) else TeleSocket()

        Chest().root[BOT_CHEST_ENTITY] = self.bot
        Chest().root.lock_filed(BOT_CHEST_ENTITY)

        self.run()

    def run(self):
        self.application.log.info(f"Logged in as @{self.bot.me.username} ({self.bot.me.id})")
        self.telesocket.login(self.config.get('TELESOCKET_TOKEN', ''))

        self.bot.remove_webhook()
        webhook = self.telesocket.set_webhook(self.bot.me.username)
        if self.config.get('SKIP_PENDING', False):
            updates_count = self.bot.skip_updates()
            if updates_count:
                log.info('Skipped {} pending messages'.format(updates_count))

        self.telesocket.add_telegram_handler(self.handle_updates)
        self.bot.set_webhook(webhook.url)

    def handle_updates(self, raw_update):
        # Serialize
        update = telebot.types.Update.de_json(raw_update)
        # Notify bot for new update
        bot.process_new_updates([update])
