import logging
import dice
from Legobot.Lego import Lego

logger = logging.getLogger(__name__)


class Roll(Lego):
    @staticmethod
    def listening_for(message):
        if message['test'] is not None:
            try:
                return message['text'].split()[0] == '!roll'
            except Exception as e:
                logger.error('Dice lego failed to check message text: %s'
                             % e)
                return False

    def handle(self, message):
        opts = None
        logger.info(message)
        try:
            target = message['metadata']['source_channel']
            opts = {'target': target}
        except IndexError:
            logger.error('Could not identify message source in message: %s'
                         % str(message))
        dice_string = message['text'].split()[1]
        results = dice.roll(dice_string)
        results_str = ', '.join([str(result) for result in results])
        txt = "You Rolled: %s" % results_str
        self.reply(message, txt, opts)

    def get_name(self):
        return 'roll'

    def get_help(self):
        help_text = "Roll some dice. Usage: " \
                    "!roll 2d6t, !roll 6d6^3, !roll d20"
        return help_text
