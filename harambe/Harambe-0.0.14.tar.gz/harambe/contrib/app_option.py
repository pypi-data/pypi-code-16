import logging
import sys
import inspect
from harambe import (db,
                   utils,
                   cache,
                   models)
from sqlalchemy.exc import SQLAlchemyError


def make_key(key):
    return utils.slugify(key)


class ApplicationOption(db.Model):
    """
    Application Option Model
    Allow to save app specific data
    """
    description = db.Column(db.String(250))
    key = db.Column(db.String(250), index=True, unique=True)
    value = db.Column(db.JSONType())
    autoload = db.Column(db.Boolean, default=False)


    @classmethod
    def get_by_key(cls, key):
        key = make_key(key)
        return cls.query().filter(key == key).first()

    @classmethod
    def get_key(cls, key):
        d = cls.get_by_key(key)
        return {} if not d else utils.dict_dot(d.value)

    @classmethod
    def set_key(cls, key, value, description=None, autoload=False):
        if not isinstance(value, dict):
            raise ValueError("AppSettings value must be a dict")
        appset = cls.get_by_key(key)
        if appset:
            data = appset.value
            data.update(value)
            upd = {
                "value": data
            }
            if description:
                upd["description"] = description
            appset.update(upd)
        else:
            cls.create(key=make_key(key),
                       value=value,
                       description=description,
                       autoload=autoload)


class AppOption(object):
    """
    Utility to access app option
    """
    def __init__(self, key, cache=True, cache_ttl=300):

        """
        :param key: string or __name__ (of the current module)
        :param cache: bool - If true it will cache the data
        :param cache_ttl: Time for the cache to live
        """
        self.key = make_key(key)
        self.cache = cache
        self.cache_ttl = cache_ttl
        self.cache_key = "__SHAFTAPPOPTION__:%s" % self.key

    def init(self, value, description, autoload=False):
        """
        Initialize a new entry if it doesn't exist
        :param value: dict
        :param description: string
        :param autoload: bool
        :return:
        """
        try:
            if not models.ApplicationOption.get_by_key(self.key):
                models.ApplicationOption.set_key(key=self.key,
                                                 value=value,
                                                 description=description,
                                                 autoload=autoload)
        except SQLAlchemyError as e:
            return None

    def set(self, value):
        """
        Set/Update data
        :param value: dict
        :return:
        """
        try:
            self._del_cache()
            models.ApplicationOption.set_key(key=self.key, value=value)
        except SQLAlchemyError as e:
            return None

    def get(self, name=None, default=None):
        """
        Get the data
        :param name: string or dot notation
        :param default: the default value if None
        :return: mixed
        """
        if not self.cache:
            return self._get()

        res = cache.get(self.cache_key)
        if not res:
            res = self._get()
            cache.set(self.cache_key, res, self.cache_ttl)
        return res.get(name, default) if name else res

    def _get(self):
        """
        Get the key from DB
        :return:
        """
        try:
            return models.ApplicationOption.get_key(key=self.key)
        except SQLAlchemyError as e:
            return None

    def _del_cache(self):
        """
        Delete the cache
        :return:
        """
        cache.delete(self.cache_key)