class BaseTag:
    tag = ''

    def __init__(self, args='', full_match='', match=None):
        self.args = args
        self.full_match = full_match
        self.match = match

    def parse(self, data):
        raise NotImplementedError

    def __str__(self):
        return 'Tag:{}'.format(self.tag or '<NONE>')


class ValueTag(BaseTag):
    """
    Simple tag
    get value from context
    {% value var_name %}
    """
    tag = 'value'

    def parse(self, data):
        if self.args:
            return data.get(self.args)
        return 'None'
