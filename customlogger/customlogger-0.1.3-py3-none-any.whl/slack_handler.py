from logging import *
import slackweb

class SlackHandler(Handler):
    EMOJIS = {
        NOTSET: ':loudspeaker:',
        DEBUG: ':simple_smile:',
        INFO: ':smile:',
        WARNING: ':sweat:',
        ERROR: ':sob:',
        CRITICAL: ':scream:'
    }

    USERNAMES = {
        NOTSET: 'Notset',
        DEBUG: 'Debug',
        INFO: 'Info',
        WARNING: 'Warning',
        ERROR: 'Erorr',
        CRITICAL: 'Critical',
    }

    def __init__(self, webhook_url, channel=None, username=None, emojis=None,
                 fmt='[%(levelname)s] [%(asctime)s] [%(name)s] - %(message)s'):
        Handler.__init__(self)
        self.__webhook_url = webhook_url
        self.__channel = channel
        self.__username = username
        self.__emojis = emojis or self.EMOJIS
        self.__fmt = Formatter(fmt)

    def setEmoji(self, levelno, emoji):
        self.__emojis[levelno] = emoji

    def setUsernames(self, levelno, username):
        self.__username[levelno] = username

    def makeContent(self, record):
        content = {
            'text': self.format(record),
            'icon_emoji': self.__emojis[record.levelno]
        }

        content['username'] = self.__username or self.USERNAMES[record.levelno]
        if self.__channel:
            content['channel'] = self.__channel
        return content

    def emit(self, record):
        try:
            slack = slackweb.Slack(self.__webhook_url)
            slack.notify(**self.makeContent(record))
        except:
            self.handleError(record)
