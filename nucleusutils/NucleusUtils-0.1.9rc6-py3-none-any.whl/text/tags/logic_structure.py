from NucleusUtils.text.tags.tags import BaseTag

SIMPLE_LOGIC = ['<', '<=', '==', '!=' '>=', '>']
LOGIC = ['and', 'or', 'not', 'in']


def check_safe(args, data):
    text = args
    for part in SIMPLE_LOGIC:
        text = text.replace(part, ' ' + part + ' ')
    text = text.strip()

    for item in text.split():
        if not ((item in SIMPLE_LOGIC or in_brackets(item)) or item in data):
            return False
    return True


def in_brackets(text):
    if (text.startswith('"') or text.startswith("'")) and (text.endswith('"') or text.endswith("'")):
        return True
    return False


class LogicElement(BaseTag):
    def parse(self, data):
        raise TypeError("tag '{}' is logic element.".format(self.tag))


class LogicIfTag(LogicElement):
    tag = 'if'

    def check(self, data):
        if not check_safe(self.args, data):
            raise SyntaxError('Wrong expression "{}"!'.format(self.args))

        env = data.copy()
        env['__builtins__'] = None
        return bool(eval(self.args, data))


class LogicElseIfTag(LogicIfTag):
    tag = 'elif'


class LogicElseTag(LogicElement):
    tag = 'else'

    def check(self, data):
        return True


class LogicEndIfTag(LogicElement):
    tag = 'endif'

    def check(self, data):
        return None


class LogicTagsStructure:
    first_tag = LogicIfTag

    body_tags = [LogicElseIfTag, LogicElseTag]
    last_tag = LogicEndIfTag

    def __init__(self, tags, text):
        self.tags = tags
        self.text = text

    def dynamic_full_match(self):
        return self.text[self.text.index(self.tags[0].full_match):self.text.index(self.tags[-1].full_match)]

    @classmethod
    def get_structures(cls, tags):
        structures = []
        group = []
        for tag in tags:
            if len(group) == 0 and isinstance(tag, cls.first_tag):
                group.append(tag)
            # elif isinstance(tag, cls.first_tag):
            #     raise SyntaxError('Can not make included logic structures')
            elif isinstance(tag, tuple(cls.body_tags)):
                group.append(tag)
            elif isinstance(tag, cls.last_tag):
                group.append(tag)
                structures.append(group.copy())
                group.clear()
        return structures

    def parse(self, data):
        for index, tag in enumerate(self.tags[:-1]):
            result = tag.check(data)
            if result:
                first_pos = self.text.index(tag.full_match) + len(tag.full_match)
                last_pos = self.text.index(self.tags[index + 1].full_match)
                return self.text[first_pos:last_pos]
        return ''
