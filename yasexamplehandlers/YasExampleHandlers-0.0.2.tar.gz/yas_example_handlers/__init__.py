import re

from yas import YasHandler
from yas_example_handlers.yaml_file_config import YamlConfiguration


class ExampleRegexHandler(YasHandler):

    def __init__(self, regexp_string, log=print):
        super().__init__(log=log)
        self.regexp = re.compile(regexp_string)
        self.log('INFO', f"{self.__class__} initialized and matching {regexp_string}!")

    def test(self, data):
        self.current_match = self.regexp.search(data.get('text'))
        return self.current_match


class ExampleCreateHandler(ExampleRegexHandler):

    def __init__(self, log=print):
        super().__init__('(?:create)\ ([-\w]+)', log=log)

    def handle(self, data, reply):
        match_groups = self.current_match.groups()
        self.__create(*match_groups, reply=reply)

    def __create(self, thing_to_create, reply=None):
        reply(f'Creating {thing_to_create}')
        self.log('INFO', f"Created {thing_to_create}")
