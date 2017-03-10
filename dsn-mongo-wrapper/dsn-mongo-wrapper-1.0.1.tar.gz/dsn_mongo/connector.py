# coding=utf-8
import logging

from pymongo import MongoClient
from pymongo.database import Database


def _get_logger():
    return logging.getLogger('dsn.mongo.connector')


class MongoConnector:
    """
    simple connector for mongodb
    """

    def __init__(self, host='127.0.0.1', port=27017, default_database=None, settings: dict = None):
        self.__logger = _get_logger()
        self.__logger.info('initializing mongodb client')
        if not default_database:
            self.__logger.warning('default database unspecified')
        self.__default_database = default_database
        self.__settings = settings
        if not self.__settings:
            self.__settings = dict()
        self.__logger.info('mongodb server host=[%s] port=[%s]', host, port)
        self.__logger.info('set replicaSet=[%s]', self.__settings.get('replicaSet', 'None'))
        self.__logger.info('set minPoolSize=[%s]', self.__settings.get('minPoolSize', 'None'))
        self.__logger.info('set maxPoolSize=[%s]', self.__settings.get('maxPoolSize', 'None'))
        self.__mongo = MongoClient(host=host, port=port, **self.__settings)

    def get_database(self, database=None) -> Database:
        if not database:
            assert self.__default_database, "default_database is None"
            database = self.__default_database
        username = self.__settings.get('username')
        password = self.__settings.get('password')
        mechanism = self.__settings.get('mechanism', 'DEFAULT')

        self.__logger.debug('get database : [%s]', database)
        db = self.__mongo.get_database(database)

        self.__logger.debug('read_preference=%s', db.read_preference.document)
        self.__logger.debug('read_concern=%s', db.read_concern.document)
        self.__logger.debug('write_concern=%s', db.write_concern.document)

        if username is not None:
            self.__logger.debug('authenticate with name:[%s]', username)
            # support authenticate with password
            assert password, "settings['password'] = None"
            db.authenticate(name=username, password=password, mechanism=mechanism)
        return db
