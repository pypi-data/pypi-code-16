import re


class Command:
    def __init__(self, args):
        self.args = args

    @classmethod
    def run(self):
        raise NotImplementedError()

    @classmethod
    def configure_argument_parser(cls, parser):
        pass

    @classmethod
    def command_name(cls):
        return '-'.join([i.lower() for i in re.findall(r'([A-Z][a-z]+)', re.sub(r'^Command', '', cls.__name__))])
