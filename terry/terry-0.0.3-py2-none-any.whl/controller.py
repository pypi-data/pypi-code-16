from __future__ import absolute_import
import sys

from datetime import datetime, timedelta
from uuid import uuid4

import pymongo

from .api import (
    Job, IJobController, IWorkerController,
    RetriableError, ConcurrencyError
)


__all__ = [u'Controller']


class Controller(IJobController, IWorkerController):
    HEARTBEAT_TIMEOUT = timedelta(minutes=10)

    def __init__(self, db_uri, col_name=u'jobs'):
        self._validate_db_uri(db_uri)
        self._client = self._create_mongo_client(db_uri)
        self._jobs = self._client.get_default_database()[col_name]
        self._ensure_indexes()

    def _create_mongo_client(self, db_uri):
        kwargs = {u'socketTimeoutMS': 10000,
                  u'readPreference': u'primary',
                  u'w': u'majority',
                  u'wtimeout': 20000,
                  u'j': True}
        # TODO:
        # We should use readConcernLevel=majority|linearizable,
        # but this requires proper configuration of MongoDB server
        return pymongo.MongoClient(db_uri, **kwargs)

    def _validate_db_uri(self, uri):
        res = pymongo.uri_parser.parse_uri(uri)
        if res[u'database'] is None:
            raise Exception(u'You should explicitly specify database')

    def _ensure_indexes(self):
        def idx(*args, **kwargs):
            keys = [(field, pymongo.ASCENDING) for field in args]
            return pymongo.IndexModel(keys, **kwargs)

        self._jobs.create_indexes([idx(u'job_id', unique=True),
                                   idx(u'job_id', u'version'),
                                   idx(u'tag', u'status', u'run_at', u'worker_heartbeat')])

    def _job_from_doc(self, doc):
        return Job(doc.pop(u'job_id'), **doc)

    def _raise_retriable_error(self, method):
        exc_type, _, _ = sys.exc_info()
        assert exc_type is not None  # should be called from the exception handler
        exc_text = u'{} has failed due to {}'.format(method, exc_type.__name__)
        raise RetriableError(exc_text)

    ########################
    #    PUBLIC METHODS    #
    ########################

    def create_job_id(self):
        return uuid4().hex

    ########################
    #    IJobController    #
    ########################

    def _update_job(self, job_id, version, **kwargs):
        query = {u'job_id': job_id, u'version': version}

        update = {u'$inc': {u'version': 1},
                  u'$set': kwargs}
        try:
            r = self._jobs.find_one_and_update(query, update, projection={u'_id': False},
                                               return_document=pymongo.collection.ReturnDocument.AFTER)
        except pymongo.errors.PyMongoError:
            self._raise_retriable_error(u'find_one_and_update')

        if r is None:
            raise ConcurrencyError(u'invalid version: {}'.format(version))

        return self._job_from_doc(r)

    def get_job(self, job_id):
        try:
            r = self._jobs.find_one({u'job_id': job_id}, projection={u'_id': False})
        except pymongo.errors.PyMongoError:
            self._raise_retriable_error(u'find_one')

        if r:
            return self._job_from_doc(r)

        return None

    def create_job(self, job_id, tag, args=None, run_at=None):
        doc = {u'job_id': job_id, u'tag': tag, u'args': args or {}, u'run_at': run_at,
               u'version': 0, u'status': Job.IDLE, u'created_at': datetime.utcnow()}
        try:
            self._jobs.insert_one(doc)
        except pymongo.errors.DuplicateKeyError:
            pass  # ok, job already exists
        except pymongo.errors.PyMongoError:
            self._raise_retriable_error(u'insert_one')

    def cancel_job(self, job_id, version):
        return self._update_job(job_id, version, status=Job.CANCELLED)

    def delete_job(self, job_id, version):
        try:
            r = self._jobs.delete_one({u'job_id': job_id, u'version': version})
        except pymongo.errors.PyMongoError:
            self._raise_retriable_error(u'delete_one')

        if r.deleted_count == 0:
            raise ConcurrencyError(u'job_id={}, version={} not found'.format(job_id, version))

        assert r.deleted_count == 1

    ###########################
    #    IWorkerController    #
    ###########################

    def _find_one_and_update(self, query, update):
        try:
            r = self._jobs.find_one_and_update(query, update, projection={u'_id': False},
                                               return_document=pymongo.collection.ReturnDocument.AFTER)
        except pymongo.errors.PyMongoError:
            self._raise_retriable_error(u'find_one_and_update')

        if r:
            return self._job_from_doc(r)

        return None

    def _try_acquire_idle_job(self, tags, worker_id):
        query = {u'tag': {u'$in': tags}, u'status': Job.IDLE,
                 u'$or': [{u'run_at': None}, {u'run_at': {u'$lt': datetime.utcnow()}}]}

        update = {u'$inc': {u'version': 1},
                  u'$set': {u'status': Job.LOCKED,
                           u'locked_at': datetime.utcnow(),
                           u'worker_id': worker_id,
                           u'worker_heartbeat': datetime.utcnow()}}

        return self._find_one_and_update(query, update)

    def _try_reacquire_locked_job(self, tags, worker_id):
        query = {u'tag': {u'$in': tags}, u'status': Job.LOCKED,
                 u'worker_heartbeat': {u'$lt': datetime.utcnow() - self.HEARTBEAT_TIMEOUT}}

        update = {u'$inc': {u'version': 1},
                  u'$set': {u'status': Job.LOCKED,
                           u'locked_at': datetime.utcnow(),
                           u'worker_id': worker_id,
                           u'worker_heartbeat': datetime.utcnow()}}

        return self._find_one_and_update(query, update)

    def acquire_job(self, tags, worker_id):
        job = self._try_acquire_idle_job(tags, worker_id)

        if job is None:
            job = self._try_reacquire_locked_job(tags, worker_id)

        if job is None:
            # there are no available jobs
            return None

        return job

    def heartbeat_job(self, job_id, version):
        return self._update_job(job_id, version, worker_heartbeat=datetime.utcnow())

    def finalize_job(self, job_id, version, worker_exception=None):
        return self._update_job(job_id, version, status=Job.COMPLETED, worker_exception=worker_exception)

    def requeue_job(self, job_id, version, run_at=None):
        return self._update_job(job_id, version, status=Job.IDLE, run_at=run_at,
                                locked_at=None, completed_at=None,
                                worker_id=None, worker_heartbeat=None)
