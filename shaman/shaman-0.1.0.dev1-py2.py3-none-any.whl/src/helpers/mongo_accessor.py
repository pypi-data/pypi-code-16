# -*- coding: utf-8 -*-

import time
import pymongo
import sys
import random

from pymongo.errors import OperationFailure,ServerSelectionTimeoutError,DuplicateKeyError, AutoReconnect, WriteError
from shaman.src.helpers.mongo_accessor_exceptions import DuplicateKeyErrorRetriesExceeded


def dict_roll(document, field_to_roll='extra',first_call=True,ignore_set=None):
    '''
    This method takes document ready for mongo upsert and rolls out inner documets with '.' for correct mongo merge
    :param document: document dict
    :param field_to_roll: field to roll_out
    :param ignore_set: set of fields which would never be rolled out
    :return: changed inplace document
    '''
    if field_to_roll not in document:
        return document

    if ignore_set:
        if field_to_roll in ignore_set:
            return document

    dict_to_roll = document[field_to_roll]

    if not type(dict_to_roll) is dict:
        return document

    keys_to_remove = [field_to_roll,]
    keys_to_add = []
    new_doc = dict()
    for k in document:
        new_doc[k] = document[k]

    for k in dict_to_roll:
        if type(dict_to_roll[k]) is dict:
            for another_k in dict_to_roll[k]:
                unrolled_dict = dict_roll(dict_to_roll[k], another_k,first_call=False, ignore_set=ignore_set)
                for unrolled_k in unrolled_dict:
                    keys_to_add.append((field_to_roll + '.' + str(k) + '.' + str(unrolled_k),unrolled_dict[unrolled_k]))
        else:
            keys_to_add.append((field_to_roll+'.'+str(k), dict_to_roll[k]))

        keys_to_remove.append(k)

    for k in keys_to_add:
        new_doc[k[0]] = k[1]

    for k in keys_to_remove:
        new_doc.pop(k,None)

    return new_doc


class MongoAccessor:
    def __init__(self,host,db,collection, time_to_reconnect,
                 n_retries = 5, update_retry_wait=3, maxPoolSize=128,
                 waitQueueMultiple=5):


        self.py_version = sys.version_info.major
        self.host = host
        self.db = db
        self.collection = collection
        self.time_to_reconnect = int(time_to_reconnect)
        self.n_retries = int(n_retries)
        self.update_retry_wait = update_retry_wait
        self.maxPoolSize = maxPoolSize
        self.waitQueueMultiple = waitQueueMultiple

        self.my_bulk = None

        self.ignore_rollout_set = set(['artm100','artm300','artm500','artm700','langs'])

        self._create_connection()

    def _create_connection(self):
        self.mongo_client = pymongo.MongoClient(host=[self.host],
                                                maxPoolSize=self.maxPoolSize,
                                                waitQueueMultiple=self.waitQueueMultiple)
        self.db = self.mongo_client[self.db]
        self.collection = self.db[self.collection]
        self.time_to_reconnect = self.time_to_reconnect

    def set_logger(self, logger):
        self.my_logger = logger

    def _update(self,id_doc, document, upsert=True, check_keys=False):
        self.collection.update_one(id_doc, document, upsert=upsert)

    def _insert(self,id_doc, document, upsert=True, check_keys=False):
        self.collection.insert_one(id_doc, document)

    def _initializeOrderedBulkOp(self):
        self.my_bulk = self.collection.initializeOrderedBulkOp()
        return self.my_bulk

    def _execute_bulk(self):
        if self.my_bulk:
            self.my_bulk.execute()
            self._initializeOrderedBulkOp()

    def execute_bulk(self):
        retries = 0

        while retries < self.n_retries:
            try:
                # if self.collection.find_one(id_doc) is not None:
                self._execute_bulk()
                # else:
                #     self._insert(id_doc, document, upsert=True, check_keys=check_keys)
                return
            except DuplicateKeyError as e:
                retries += 1
                self.my_logger.error('Mongo DuplicateKeyError catched, retrying to update. Current retry: {}' \
                                     .format(retries))
                time.sleep(self.update_retry_wait * random.random())
            except AutoReconnect as e:
                retries += 1
                self.my_logger.error('Mongo AutoReconnect catched, retrying to update. Current retry: {}' \
                                     .format(retries))
                time.sleep(self.update_retry_wait * random.random())


    def update(self, id_doc, document, check_keys=False):
        retries = 0

        # a little mess here
        if '$set' in document:
            document['$set'] = dict_roll(document['$set'], 'extra', ignore_set=self.ignore_rollout_set) # doing changes in-place, rolling out dict of dicts as extra.key1.key2:value, ... so on

        while retries < self.n_retries:
            try:
                # if self.collection.find_one(id_doc) is not None:
                if self.my_bulk:
                    self.my_bulk.update(id_doc, document, upsert=True, check_keys=check_keys)
                else:
                    self._update(id_doc, document, upsert=True, check_keys=check_keys)
                # else:
                #     self._insert(id_doc, document, upsert=True, check_keys=check_keys)
                return
            except DuplicateKeyError as e:
                retries+=1
                self.my_logger.error('Mongo DuplicateKeyError catched, retrying to update. Current retry: {}'\
                                     .format(retries))
                time.sleep(self.update_retry_wait*random.random())
            except AutoReconnect as e:
                retries += 1
                self.my_logger.error('Mongo AutoReconnect catched, retrying to update. Current retry: {}' \
                                     .format(retries))
                time.sleep(self.update_retry_wait * random.random())


            except WriteError as e:
                if 'key too large to index' in str(e):
                    if self.py_version == 2:
                        try:
                            self.my_logger.error(u'Mongo WriteError catched, key too large to index, key is {}'.format(
                                id_doc['_id']))
                        except UnicodeDecodeError as e:
                            self.my_logger.error('Mongo WriteError catched, key too large to index, key is {}'.format(
                                id_doc['_id']))

                    else:
                        try:
                            self.my_logger.error(u'Mongo WriteError catched, key too large to index, key is {}'.format(
                                id_doc['_id']))
                        except UnicodeDecodeError as e:
                            self.my_logger.error('Mongo WriteError catched, key too large to index, key is {}'.format(
                                id_doc['_id']))
                else:
                    raise e
                return


        raise DuplicateKeyErrorRetriesExceeded()

