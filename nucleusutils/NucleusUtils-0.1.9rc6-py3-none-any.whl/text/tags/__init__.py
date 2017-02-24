import re

from NucleusUtils.text.tags.logic_structure import LogicIfTag, LogicElseIfTag, LogicElseTag, LogicEndIfTag, \
    LogicTagsStructure

# TODO: Remove all this shit. Use jinja2

TAG_BRACKETS = ['{%', '%}']

TAG_PATTERN = re.compile('(?P<full>' + TAG_BRACKETS[0] +
                         ' (?P<command>[a-zA-Z0-9_]+)(?: (?P<args>(?!' + TAG_BRACKETS[1] + ')[\w\W]*?))? ' +
                         TAG_BRACKETS[1] + ')')

BUILTIN_TAGS = {
    'if': LogicIfTag,
    'elif': LogicElseIfTag,
    'else': LogicElseTag,
    'endif': LogicEndIfTag
}

BUILTIN_STRUCTURES = [
    LogicTagsStructure
]


def compile_pattern(text, tags, global_vars=None, local_vars=None, structures=None, wrong=''):
    if global_vars is None:
        global_vars = {}
    if local_vars is None:
        local_vars = {}
    if structures is None:
        structures = {}
    local_tags = []
    for match in TAG_PATTERN.finditer(text):
        full_match, tag, args = match.groups()
        if tag in tags:
            local_tags.append(tags[tag](args, full_match, match))
    return CompiledParser(text, local_tags, global_vars, local_vars, structures, wrong)


class Parser:
    def __init__(self, tags=None, global_vars=None, structures=None):
        if tags is None:
            tags = []
        if global_vars is None:
            global_vars = {}
        self.tags = {tag.tag: tag for tag in tags}
        self.globals = global_vars
        self.structures = BUILTIN_STRUCTURES

        if structures is not None:
            for structure in structures:
                if structure not in self.structures:
                    self.structures.append(structure)

        self.tags.update(BUILTIN_TAGS)

    def add_tag(self, tag):
        if tag.tag in BUILTIN_TAGS:
            raise KeyError(tag.tag)
        self.tags[tag.tag] = tag

    def compile(self, text, local_vars=None, wrong=''):
        return compile_pattern(text, self.tags, self.globals, local_vars, self.structures, wrong)


class CompiledParser:
    def __init__(self, text, tags=None, global_vars=None, local_vars=None, structures=None, wrong=''):
        if structures is None:
            structures = []
        if tags is None:
            tags = []
        if global_vars is None:
            global_vars = {}
        if local_vars is None:
            local_vars = {}
        self.text = text
        self.tags = tags
        self.vars = global_vars
        self.vars.update(local_vars)
        self.wrong = wrong
        self.structures = structures
        self.compiled_structures = []

    @property
    def result(self):
        if not hasattr(self, '__result'):
            self.generate()
        return getattr(self, '__result')

    def generate(self):
        setattr(self, '__result', self.__generate())

    def __parse_structures(self, raw_text):
        text = raw_text
        for structure in self.structures:
            for raw_struct in structure.get_structures(self.tags):
                struct = LogicTagsStructure(raw_struct, self.text)
                text = text.replace(struct.dynamic_full_match(), struct.parse(self.vars))
                self.compiled_structures.append(struct)
                for tag in struct.tags:
                    self.tags.remove(tag)

        return text

    def __generate(self):
        if not len(self.tags):
            return self.text

        result = self.text
        result = self.__parse_structures(result)
        for tag in self.tags:
            try:
                result = result.replace(tag.full_match, tag.parse(self.vars))
            except (SyntaxError, TypeError) as e:
                return 'Extepion: ' + str(e)
            except:
                self.tags.remove(tag)
        if self.wrong is not None:
            for tag in TAG_PATTERN.finditer(result):
                result = result.replace(tag.groups()[0], self.wrong)
        return result

    def __str__(self):
        return self.result
