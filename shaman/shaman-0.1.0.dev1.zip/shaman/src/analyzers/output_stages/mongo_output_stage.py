from bson.errors import InvalidStringData
from shaman.src.analyzers.abstract_stage import AbstractStage
from shaman.src.helpers.mongo_accessor import MongoAccessor


class MongoOutputStage(AbstractStage):
    def init_stage(self):
        self.document_field = self.config['document_field']

        self.document_id_field = None

        if 'document_id_field' in self.config:
            self.document_id_field = self.config['document_id_field']

        self.mongo_collection = MongoAccessor(host=self.config['mongohost'],
                                          db=self.config['db'],
                                          collection=self.config['collection'],
                                          time_to_reconnect=int(self.config['time_reconnect']),
                                          n_retries=int(self.config['n_retries']),
                                          update_retry_wait=float(self.config['update_retry_wait']))

    def set_logger(self, logger):
        self.my_logger = logger
        self.mongo_collection.set_logger(self.my_logger)

    def do_stage(self,  message):
        if self.document_field in message.results:
            document = message.results[self.document_field]

            if self.document_id_field:
                if self.document_id_field in message.__dict__:
                    if self.document_id_field!='_id':
                        document['_id'] = message.__dict__[self.document_id_field]
                else:
                    raise NotImplementedError()

            try:
                doc_id = document['_id']

                if document:
                    if 'inc_field' in message.__dict__:
                        self.mongo_collection.update({'_id': doc_id},
                                                    {"$set": document,
                                                     "$inc":{message.inc_field:1}})
                    else:
                        self.mongo_collection.update({'_id': doc_id},
                                                     {"$set": document})

            except InvalidStringData as e:
                self.my_logger.error("InvalidStringData exception catched. "
                                     "Trying to decode a message and update again. Url: {}".format(document['_id']))

                document['_id'] = document['_id'].decode("cp1251").encode("utf8")
                self.mongo_collection.update({'_id': document['_id']},
                                             {"$set": document})

        else:
            self.my_logger.warning('MongoOutputStage: field {} not found in message.results'.format(self.document_field))