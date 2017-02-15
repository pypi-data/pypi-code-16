# coding:utf-8

import uuid

def uniqueid(bit=64):
   """获取64位requesid"""

   return uuid.uuid1().int>>bit


class Base(object):

    @staticmethod
    def enum(**enums):
        return type('Enum',(),enums)

    @staticmethod
    def check_arguments(keys,essential_keys):
        keys = set(keys)
        essential_keys = set(essential_keys)
        
        if keys == essential_keys:
            return False

        if keys == essential_keys:
            return False

        if keys.issuperset(essential_keys):
            return True
        else:
            return False

    @staticmethod
    def isset(v):
        try:
            type(eval(v))

        except:
            return False
        else:
            return True
    @staticmethod
    def empty(s):
        return True if 0 == len(s) else False

    @staticmethod
    def md5(s):
        md = hashlib.md5()
        md.update(s)
        return md.hexdigest()

