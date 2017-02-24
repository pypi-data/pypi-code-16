from NucleusUtils.i18n.text_utils import get_num_ending

FIRST_TAG_SYMBOL = '{'
LAST_TAG_SYMBOL = '}'
ESCAPE_SYMBOL = '\\'

parsers = []


def add_parser(parser):
    assert isinstance(parser, BaseParser)
    if parser not in parsers:
        parsers.append(parser)


def get_raw_tags(text):
    """
    Get tags from text
    :param text:
    :return:
    """
    start_pos = -1
    escape = -1
    for pos, symbol in enumerate(text):
        # Enable escaping
        if symbol == ESCAPE_SYMBOL and escape < 0:
            escape = pos

        # First symbol
        if symbol == FIRST_TAG_SYMBOL and escape < 0:
            start_pos = pos
            continue

        # Finish symbol - return result
        if symbol == LAST_TAG_SYMBOL and escape < 0:
            yield text[start_pos:pos + 1]
            start_pos = -1

        if escape < pos:
            escape = -1


class Keyword:
    def __init__(self, raw, command, params):
        self.raw = raw
        self.command = command
        self.params = params

    @classmethod
    def parse(cls, tag):
        keyword = tag[1:-1]
        command = None
        params = []
        temp_pos = 0
        for pos, symbol in enumerate(keyword):
            if symbol == ':' and command is None:
                command = keyword[temp_pos:pos].strip()
                temp_pos = pos + 1
            if symbol == '|':
                params.append(keyword[temp_pos:pos].strip())
                temp_pos = pos + 1
            if pos + 1 == len(keyword):
                if command is None and not len(params):
                    command = keyword[temp_pos:pos + 1]
                else:
                    params.append(keyword[temp_pos:pos + 1].strip())
        return cls(tag, command, params)

    def __str__(self):
        return '{}({})'.format(self.command, ', '.join(self.params))

    def __repr__(self):
        return str(self)


class BaseParser:
    """
    Skeleton for parsers
    """

    def check(self, keyword, settings):
        """
        Validate tag
        :param keyword:
        :return:
        """
        raise NotImplementedError

    def generate_result(self, keyword, settings):
        """
        Need to override this method
        :param keyword:
        :param settings:
        :return:
        """
        raise NotImplementedError

    def parse(self, text, keyword, settings):
        """
        Parse (replace)
        :param text:
        :param keyword:
        :param settings:
        :return:
        """
        return text.replace(keyword.raw, str(self.generate_result(keyword, settings)))


class SimpleFormatParser(BaseParser):
    """
    Analog of str.format() but without parameters and cat parse only key-value based keywords
    Not safe with some other parsers
    """

    def generate_result(self, keyword, settings):
        return settings.get(keyword.command) or '{' + str(keyword.command or '') + '}'

    def check(self, keyword, settings):
        return True


class ConstantParser(BaseParser):
    def __init__(self, context):
        self.context = context

    def check(self, keyword, settings):
        if keyword.command in self.context:
            return True
        return False

    def generate_result(self, keyword, settings):
        return self.context.get(keyword.command)


class NumEndingsParser(BaseParser):
    def check(self, keyword, settings):
        if 3 <= len(keyword.params) <= 4 and (keyword.command is None or keyword.command in settings):
            return True
        return False

    def generate_result(self, keyword, settings):
        count = settings.get(keyword.command or 'count') or 0
        if len(keyword.params) == 4:
            if count == 0:
                return keyword.params[0].replace('#', str(count))
            return get_num_ending(count, keyword.params[1:]).replace('#', str(count))
        return get_num_ending(count, keyword.params).replace('#', str(count))
