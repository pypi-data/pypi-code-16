import json

class OptionalStringConverter(object):

    @staticmethod
    def build_from_json(j_str):
        '''Produce a string object from deserialized server response for optional string

        Input like '{'value': 'foo'}'

        Parameters
        ----------
        :type j_str: dict or json-encoded string representing a JSON object

        Returns
        -------
        :type string or None
        '''
        result = None

        if not isinstance(j_str, dict):
            j_str = json.loads(j_str)

        if 'value' in j_str:
            result = j_str.pop('value', result)

        return result
