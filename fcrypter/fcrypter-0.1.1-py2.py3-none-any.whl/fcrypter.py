# -*- coding: utf-8 -*-
from __future__ import absolute_import
import string
from fcrypter import aes

all_chars = string.ascii_letters + string.punctuation


def pad_key(key, cipher):
    """
    Adds extra characters to a key to reach the maximum supported key length
    :param key: encryption key
    :type cipher: Cryptor
    :return: str
    """
    return "{}{}".format(key, cipher.generate_random_password(
        size=max(cipher.supported_sizes) - len(key), chars=all_chars))


def get_aes_supported_modes():
    """
    Returns a named tuple with supported AES cipher modes and their class
    name callback
    """
    return {'AES-EAX': aes.AESCryptorEAX}


def get_supported_ciphers():
    """
    Returns a list of named tuples with supported cipher name and callback
    class name
    :rtype: dict
    """
    return get_aes_supported_modes()
