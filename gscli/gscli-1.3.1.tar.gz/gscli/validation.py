from prompt_toolkit.validation import ValidationError, Validator
from gnusocial.utils import DOMAIN_REGEX
from . import commands
from .i18n import _


TEMPLATE = _('Unknown command: \'{cmd}\'')
class CommandValidator(Validator):
    def validate(self, document):
        if document.text:
            cmd, *args = commands.split(document.text)
            if cmd not in commands.commands:
                raise ValidationError(message=TEMPLATE.format(cmd=cmd))
            else:
                if hasattr(self, cmd):
                    self.__getattribute__(cmd)(args, document)

    @staticmethod
    def help(args, document):
        for arg in args:
            if arg not in commands.commands:
                i = document.text.find(arg)
                raise ValidationError(i, 'help: ' + TEMPLATE.format(cmd=arg))


class URLValidator(Validator):
    def validate(self, document):
        if not DOMAIN_REGEX.match(document.text):
            raise ValidationError(message=_('Invalid server URL'))
