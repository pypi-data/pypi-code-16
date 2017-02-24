# coding=utf8

import hashlib
import random
import sys


def gen_rnd():
    """
    generate random salt
    :return:
    :rtype:
    """
    return "".join(random.sample('1qazxsw23edcvfr45tgbnhy67ujmki89olp0QAZXWEDCVFRTGBNHYUJMKIOPL' * 6, 64))


class Salted(object):
    """
    useage:

    first step:

        import hashlib
        from saltedpwd import Salted
        salted = Salted(hashlib.sha256)

    now, you can get hashed password by:

        password = salted.gen_password('YOUR PASSWORD')

    and, verify your input by:

        if salted.verify_password('PASSWORD INPUT', 'PASSWORD HASHED'):
            # password correct
        else:
            # password not correct

    """
    def __init__(self, hash_function):
        """
        init with hash method
        :param hash_function:hash method,for example from hashlib import sha256
        :type hash_function:
        """
        self.hash_func = hash_function

    def gen_password(self, raw_password):
        """
        generate salted password by random salt
        :param raw_password:
        :type raw_password:
        :return:
        :rtype:
        """
        salt = gen_rnd()
        origin_str = ":".join([salt, raw_password])
        hashed_str = self.hash_func(origin_str).hexdigest()
        return "".join([salt, hashed_str])


    def verify_password(self, raw_password, hashed_password):
        """
        verify password if correct input
        :param raw_password:
        :type raw_password:
        :param hashed_password:
        :type hashed_password:
        :return:
        :rtype:
        """
        salt, hash_str = hashed_password[:64], hashed_password[64:]
        origin_str = ":".join([salt, raw_password])
        hashed_str = self.hash_func(origin_str).hexdigest()
        return hash_str == hashed_str


def hash_pwd():
    if len(sys.argv) < 2:
        raw_pass = raw_input('input raw password')
    else:
        raw_pass = sys.argv[1]
    print Salted(hashlib.sha256).gen_password(raw_pass)


def verify_pwd():
    if len(sys.argv) < 2:
        raw_pass = raw_input('input raw password')
    else:
        raw_pass = sys.argv [1]
    if len(sys.argv) < 3:
        hashed_pass = raw_input('input hashed password')
    else:
        hashed_pass = sys.argv [1]
    print Salted(hashlib.sha256).verify_password(raw_pass, hashed_pass)
