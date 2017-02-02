from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime, timedelta
from copy import deepcopy
from bson import ObjectId

class Queue(object):

    '''
        initialize queue object. A queue is a mongo collection where records
        awaiting progress are kept. The queue object is the gateway for
        interacting with a queue.
    '''

    def __init__(self, db, queueName):

        """
            Setup initial queue; create new record in 'queueList' if does not already exist

            :param MongoClient db: MongoDB connection
            :param string queueName: Name of queue
        """

        if queueName in ['queueList', 'batchList']:
            raise ValueError('Queue name \'' + queueName + '\' is reserved')

        self.queueName = queueName

        self.queue = db[self.queueName]

        self.db = db

        ## check if an instance already exists
        queueFind = db['queueList'].find_one({'queueName': queueName})

        if queueFind:

            self._id = queueFind['_id']

        else:
            ## create a new instance
            queueNew = db['queueList'].insert_one({'queueName': queueName})
            self._id = queueNew.inserted_id

    def getQueueSize(self):

        """
            Returns count of records in queue
        """

        return self.queue.count()

    def getQueueStats(self):

        """
            Returns set of queue stats including max/min _counter, max/min _timestamp
        """

        stats = {}
        stats['_counter'] = {}
        stats['_timestamp'] = {}

        size = self.queue.count()

        if size>0:
            stats['_counter']['max'] = self.queue.find_one({},
                                                           sort=[('_counter',
                                                                  DESCENDING)]
                                                           )['_counter']
            stats['_counter']['min'] = self.queue.find_one({},
                                                           sort=[('_counter',
                                                                  ASCENDING)]
                                                           )['_counter']

            stats['_timestamp']['min'] = (datetime.now() - self.queue.find_one({}, sort=[('_timestamp', DESCENDING)])['_timestamp']).total_seconds()
            stats['_timestamp']['max'] = (datetime.now() - self.queue.find_one({}, sort=[('_timestamp', ASCENDING)])['_timestamp']).total_seconds()
        else:
            stats['_counter']['max'] = 0
            stats['_counter']['min'] = 0

            stats['_timestamp']['min'] = 0
            stats['_timestamp']['max'] = 0

        return stats

    def getAvailSize(self):

        """
            Returns count of records not currently locked (i.e., the number of records a new job could start processing)
        """

        return self.queue.count({'_jobName': '', '_lockTimestamp': ''})

    def getNextBatch(self):

        """
            Returns id of next batch to process, sorted first by priority then by age
        """

        oldest_record = self.queue.find_one({'_jobName': '', '_lockTimestamp': ''}, sort=[('_priority', DESCENDING), ('_timestamp', ASCENDING)])

        if oldest_record is not None:
            return oldest_record['_batchID']
        else:
            return None

    def add(self, item, batchName='', priority=False, transfer=False, batchCustom={}):

        """
            Add records to a queue for processing, and, if specified, creates a new batch.
            Returns batch ID and count if batch name specified, else returns count

            :param list item: list of dictionaries to add to queue
            :param dict item: single dictionary record to add to queue
            :param string batchName: optional, create new batch to which records are associated
            :param bool priority: If True, process these records before others
            :param bool transfer: If True, preserve system id field of record across queues to prevent duplication from potential multiple threads
            :param dict batchCustom: optional, adds a set of custom fields to batch record in `batchList`
        """

        if type(item) == dict:
            item = [item]

        if len(item)>0:

            if batchName!='':
                newBatch = Batch(batchName=batchName, batchCount=len(item), batchCustom=batchCustom, db=self.db)
                batchID=newBatch.batchID
            else:
                batchID=''

            for row in item:
                row['_timestamp'] = datetime.now()
                row['_counter'] = 0
                row['_jobName'] = ''
                row['_lockTimestamp'] = ''
                if priority:
                    row['_priority'] = 1
                else:
                    row['_priority'] = 0
                if not transfer:
                    row['_batchName'] = batchName
                    row['_batchID'] = batchID
                    if '_id' in row:
                        del row['_id']

            if transfer:
                ids = []
                for row in item:
                    result = self.queue.update_one({'_id': row['_id']}, {'$set': row}, upsert=True)
                    ids.append(row['_id'])
                idlen = len(ids)

            else:
                result = self.queue.insert_many(item)
                idlen = len(result.inserted_ids)

            if batchName!='':
                returnSet = {}
                returnSet['_insertedCount'] = idlen
                returnSet['_batchID'] = batchID

                return returnSet
            else:
                return idlen

        else:

            return 0

    def next(self, job, limit=1, batchID=None):

        """
            Returns next record(s) to be processed and places a lock to prevent re-processing

            :param string job: job name under which to lock record(s)
            :param int limit: max count of records to return
            :param string batchID: system id of batch
        """

        if batchID is None:
            res = self.queue.find({'_jobName': '', '_lockTimestamp': ''}, limit = limit, sort=[('_priority', DESCENDING)])
        else:
            res = self.queue.find({'_jobName': '', '_lockTimestamp': '', '_batchID': batchID}, limit = limit, sort=[('_priority', DESCENDING)])

        res_id = []

        records = []

        for row in res:

            records.append(row)

            res_id.append(row['_id'])

        lock = self.queue.update_many({'_id': {'$in': res_id}},
                                      update = {'$set':
                                                {'_jobName': job,
                                                 '_lockTimestamp': datetime.now()},
                                                '$inc': {'_counter': 1}})

        return records

    def release(self, release):

        """
            Purposefully release locked records to be picked up by another job/instance

            :param list release: set of records (output from `next`) to release back into queue
        """

        result = self.queue.update_many({'_id': {'$in': [d['_id'] for d in release]}}, {'$set': {'_jobName': '', '_lockTimestamp': ''}})

        return result.modified_count

    def timeout(self, t=300):

        """
            Force-release locked records with lock time older than specified age to be picked up by another job/instance

            :param int t: age (in seconds) for records to release
        """

        result = self.queue.update_many({'_lockTimestamp': {'$lt': datetime.now() - timedelta(seconds=t)}}, {'$set': {'_jobName': '', '_lockTimestamp': ''}})

        return result.modified_count

    def cleanup(self, n=30):

        """
            Delete queue records after a certain number of processing attempts

            :param int n: value for `_counter` to delete by
        """

        result = self.queue.delete_many({'_counter': {'$gte': n}})

        return result.deleted_count

    def complete(self, records, completeBatch=False):

        """
            Remove records from queue; optionally update batch record with completion count (useful if a batch has to travel between several queues)

            :param list records: list of records (output from `next`) to complete
            :param bool completeBatch: if True, updates each batch from record set with count of records completed
        """

        if completeBatch:

            batchSet = {}
            for record in records:
                if record['_batchID'] in batchSet:
                    batchSet[record['_batchID']] += 1
                else:
                    batchSet[record['_batchID']] = 1

            for batch in batchSet:

                self.db.batchList.update_one({'_id': batch}, {'$inc': {'completeCount': batchSet[batch]}})
                self.db.batchList.update_one({'_id': batch, '$where': 'this.batchCount==this.completeCount'}, {'$set': {'isComplete': True, 'completedTimestamp': datetime.now()}})

        result = self.queue.delete_many({'_id': {'$in': [d['_id'] for d in records]}})
        return result.deleted_count

class Batch(object):

    """
        Class wrapper for Batch object; used to create and interact with new batches
    """

    def __init__(self, db, id=None, batchName=None, batchCount=None, batchCustom={}):

        """
            Init new Batch object

            :param string batchName: name of batch
            :param int batchCount: Count of records added with batch
            :param MongoClient db: MongoDB connection
            :param dict batchCustom: Dict of custom fields to add at a batch level
        """
        self.db = db

        if id:
            batch = db['batchList'].find_one({'_id': ObjectId(id)})
            if not batch:
                raise KeyError('Invalid batch ID')

            self.batchName = batch['batchName']
            self.batchCount = batch['batchCount']
            self.batchID = id
            self.timestamp = batch['timestamp']
            self.completeCount = batch['completeCount']
            self.isComplete = batch['isComplete']
            self.custom = batch['custom']
        else:
            self.batchName = batchName
            self.batchCount = batchCount

            insertBatch = db['batchList'].insert_one({'batchName': batchName,
                                                      'batchCount': batchCount,
                                                      'timestamp': datetime.now(),
                                                      'completeCount': 0,
                                                      'isComplete': False,
                                                      'custom': batchCustom})

            self.batchID = insertBatch.inserted_id

    def update_custom(self, data):

        temp_data = {}
        for key in data.keys():
            newkey = 'custom.' + key
            temp_data[newkey] = data[key]

        upd = self.db['batchList'].update_one({'_id': ObjectId(self.batchID)},
                                              {'$set': temp_data})

        if upd.modified_count==1:
            # re-initialize with updated custom data
            self.__init__(db=self.db, id=self.batchID)
            return True
        else:
            return False

def clean(data, removeBatch=False):

    """
        Remove queue and batch-specific system fields from set of queue records

        :param list data: list of records (output from `next`) from which to remove system fields
        :param bool removeBatch: If True, also remove batch-specific fields
    """

    dataClean = deepcopy(data)

    for row in dataClean:
        del row['_id']
        del row['_counter']
        del row['_timestamp']
        del row['_lockTimestamp']
        del row['_jobName']
        del row['_priority']
        if removeBatch:
            del row['_batchID']
            del row['_batchName']

    return dataClean
