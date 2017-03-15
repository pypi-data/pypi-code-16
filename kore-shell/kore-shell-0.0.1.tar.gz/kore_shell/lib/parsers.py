class KVParser(object):

    def __init__(self, kv_sep='=', keys_sep='.'):
        self.kv_sep = kv_sep
        self.keys_sep = keys_sep

    def parse(self, kv):
        """
        Parses key value string into dict

        Examples:
            >> parser.parse('test1.test2=value')
            {'test1': {'test2': 'value'}}

            >> parser.parse('test=value')
            {'test': 'value'}
        """
        key, val = kv.split(self.kv_sep, 1)
        keys = key.split(self.keys_sep)
        for k in reversed(keys):
            val = {k: val}
        return val
