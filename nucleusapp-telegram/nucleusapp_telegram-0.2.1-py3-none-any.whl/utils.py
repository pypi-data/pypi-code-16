from NucleusApp.chest import Chest

from .base import TelegramBot

BOT_CHEST_ENTITY = 'bot'


def get_bot() -> TelegramBot:
    """
    Get bot instance
    :return:
    """
    bot = Chest().root.get(BOT_CHEST_ENTITY)
    if not bot:
        raise RuntimeError('Cannot get bot instance before it will be declared')
    return bot
