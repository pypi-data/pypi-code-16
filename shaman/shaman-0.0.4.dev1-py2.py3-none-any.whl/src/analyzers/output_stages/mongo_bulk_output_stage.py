from bson.errors import InvalidStringData
from shaman.src.analyzers.abstract_stage import AbstractStage
from shaman.src.helpers.mongo_accessor import MongoAccessor


class MongoOutputStage(AbstractStage):
    def init_stage(self):
        self.document_field = self.config['document_field']
        self.bulk_flush_count = int(self.config['bulk_flush_count'])
        self.bulk_counter = 0

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
            try:
                if self.bulk_counter%self.bulk_flush_count == 0:
                    self.mongo_collection.execute_bulk()
                    self.mongo_collection.initializeOrderedBulkOp()
                    self.bulk_counter = 0

                self.bulk.update({'_id': document['_id']},
                                 {"$set": document})

                self.bulk_counter+=1

            except InvalidStringData as e:
                self.my_logger.error("InvalidStringData exception catched. Trying to decode a message and update again. Url: {}".format(document['_id']))
                document['_id'] = document['_id'].decode("cp1251").encode("utf8")
                self.mongo_collection.update({'_id': document['_id']},
                                             {"$set": document})

        else:
            self.my_logger.warning('MongoOutputStage: field {} not found in message.results'.format(self.document_field))

    def finish_batch(self):
        if self.bulk_counter!=0:
            self.bulk.execute()

    def shutdown(self):
        pass