"""Database management for web api.
"""

import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
import commentjson


class VisualObject(object):
  pass

class MongoManager(object):

    # data
    client = None
    db = None
    collection = None

    def __init__(self):
        pass

    def load_config(self, config_fn):
        with open(config_fn, 'r') as f:
            str = f.read()
            configs = commentjson.loads(str)
        self.mongo_dir = configs['mongodb']['root_folder']
        self.host_name = configs['database']['host_name']
        self.host_port = configs['database']['host_port']
        self.db_name = configs['database']['db_name']
        self.collection_name = configs['database']['collection_name']
        print 'mongodb config file loaded.'

    def check_connection_valid(self):
        if self.client == None or \
        self.db == None or \
        self.collection == None:
            print 'db connection invalid'
            return False
        else:
            return True
    
    def connect(self):
        self.client = MongoClient('mongodb://' + self.host_name + ':' + self.host_port + '/')
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]
        print 'mongodb connected.'

    def disconnect(self):
        self.client.close()

    def retrieve(self, objids):
        if not self.check_connection_valid():
            return
        res = []
        for id in objids:
            doc = self.collection.find_one({'_id': ObjectId(id)})
            res.append(doc)
        return res
    
    # set new value to a field
    def update(self, query, field, new_value):
        try:
            update_res = self.collection.update_one(
                query,
                {
                    '$set': {
                        field: new_value
                    }
                }
            )
        except pymongo.errors.PyMongoError as ex:
            print 'error {}'.format(ex)


if __name__ == '__main__':
    dm = MongoManager()
    config_fn = 'E:/Projects/Github/VisualSearchEngine/Owl/Settings/engine_settings2.json'
    dm.load_config(config_fn)