# -*- coding:utf-8 -*-

from pymongo import MongoClient

CONF_RAESE = """
from lawes.db import models
models.setup(conf={'mongo_uri': 'mongodb://127.0.0.1:27017/test', 'conn_index': 'testindex'})
"""

class QuerySet(object):

    def __init__(self):
        self._mongo = None
        self.conn_index = ''

    def _insert(self, obj_class, obj):
        """ 数据库中插入数据，到这里 Model.save() 才算真正完成
            return _id
        """
        collection = self.get_collection(obj_class=obj_class)
        return collection.insert(obj.to_dict())

    def _update(self, obj_class, obj):
        """ 数据库中更新数据，到这里 Model.save() 才算真正完成
            return _id
        """
        collection = self.get_collection(obj_class=obj_class)
        update_dict = obj.to_dict(fields='save_fields')
        update_dict.pop('_id')
        return collection.update({'_id': obj._id }, {'$set': update_dict }, upsert=True)

    def _get_collection_name(self, obj_class):
        return obj_class.__module__.split('.')[-1] + '_' + obj_class.__name__.lower()

    @property
    def mongo(self):
        if not self._mongo or not self.conn_index:
            raise CONF_RAESE
        return self._mongo

    def get_collection(self, obj_class):
        db = self.conn_index
        db = db.lower()
        db = self.mongo[db]
        collection_name = self._get_collection_name(obj_class=obj_class)
        collection = getattr(db, collection_name)
        return collection

    def _setup(self, conf):
        """ 设置mongodb的连接方式
        """
        if self._mongo:
            return
        if self.conn_index:
            return
        if not 'conn_index' in conf:
            raise CONF_RAESE
        if not 'mongo_uri' in conf:
            raise CONF_RAESE
        self._mongo = MongoClient(conf['mongo_uri'])
        self.conn_index = conf['conn_index']

    @classmethod
    def init_index(cls):
        # TODO
        index = cls.index
        if not index:
            return
        collection = cls.get_collection()
        try:
            old_index = collection.index_information()
        except:
            return
        for ikey in index:
            if not ikey + '_1' in old_index:
                unique = index[ikey].get('unique',False)
                if unique is True:
                    collection.ensure_index(ikey, unique=True)
                else:
                    collection.ensure_index(ikey)

    def get_multi(self, obj_class, **query):
        """ 获得多个数据
        """
        collection = self.get_collection(obj_class=obj_class)
        multi_data = collection.find(query)
        return multi_data

queryset = QuerySet()