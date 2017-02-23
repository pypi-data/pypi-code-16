"""Byte data types."""


class Dictionary(object):
    """Property dictionary type."""

    def __init__(self, key_type, value_type):
        """
        Create property dictionary type.

        :param key_type: Key type
        :type key_type: object

        :param value_type: Value type
        :type value_type: object
        """
        self.key_type = key_type
        self.value_type = value_type


class List(object):
    """Property list type."""

    def __init__(self, value_type):
        """
        Create property list type.

        :param value_type: Value type
        :type value_type: object
        """
        self.value_type = value_type
