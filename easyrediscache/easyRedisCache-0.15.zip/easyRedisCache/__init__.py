from __future__ import with_statement
import sys
import inspect

import redis
import pickle

import sherlock
from sherlock import Lock, LockTimeoutException

class easyRedisCache():
	def __init__(self, prefix, **kwargs):
		self.prefix = str(prefix)
		self.lockprefix = 'lock'
		self.locks = {}
		self.r = redis.StrictRedis(host='10.8.2.1', port=6379, db=1)
		
		self.retry = 5
		timeout = 5
		retry_interval = 0.01

		for k in kwargs:
			if k == "redisClient":
				self.r = kwargs[k]
			elif k == "retry_interval":
				retry_interval = kwargs[k]
			elif k == "timeout":
				retry_interval = kwargs[k]
			elif k == "retry":
				self.retry = kwargs[k]
			
		sherlock.configure(timeout=timeout, retry_interval=retry_interval, backend=sherlock.backends.REDIS)
		sherlock.configure(client=self.r)

	def _generate_index(self, index):
		return self.prefix + "/"+ str(index)

	def _generate_lock_index(self, index):
		return self.prefix + "/"+ self.lockprefix +  "/"+ str(index)

	def _get(self, index):
		data = self.r.get(self._generate_index(index))
		if data != None:
			return(pickle.loads(data))
		else:
			return data

	def get(self, index):
		if self.locked(index) == True:
			if self.lock(index) != None:
				data = self._get(index)
				self.releaseLock(index)
		else:
			data = self._get(index)
		return data

	def _set(self, index, value):
		return self.r.set(self._generate_index(index), pickle.dumps(value))

	def set(self, index, value):
		if self.lock(index) != None:
			self._set(index, value)
			self.releaseLock(index)

	def delete(self, index):
		if self.lock(index) != None:
			self.r.delete(self._generate_index(index))
			self.releaseLock(index)

	def releaseLock(self, index):
		index = self._generate_lock_index(index)
		self._releaseLock(self.locks[index])
		del self.locks[index]

	def _releaseLock(self, lock):
		lock.release()

	def _lock(self, lock):
		lock.acquire()

	def lock(self, index):
		index = self._generate_lock_index(index)
		lock = Lock(index)

		ready = False
		rounds = 0

		while ready == False:
			try:
				self._lock(lock)
				self.locks[index] = lock
			except LockTimeoutException:
				if rounds < self.retry:
					rounds += 1
				else:
					del self.locks[index]
					lock = None
					ready = True
			else:
				ready = True

		return lock

	def locked(self, index):
		index = self._generate_lock_index(index)
		if index in self.locks:
			lock = self.locks[index]
		else:
			lock = Lock(index)
		return lock.locked()

	def setBlocking(self, index, get=False):
		return self._setBlocking(self, index, get)

	class _setBlocking():
		def __init__(self, easyCache, index, get):
			self.index = index
			self.easyCache = easyCache
			self.val = None
			self.get = get
			self.exception = None

		def __enter__(self):
			if self.easyCache.lock(self.index) != None:			    
				if self.get == True:
					self.val = self.easyCache._get(self.index)
			else:
				self.exception = "LockTookTooLong"
			return self

		def __exit__(self, type, value, traceback):
			if self.exception == None and type == None:
				self.easyCache._set(self.index, self.val)
				self.easyCache.releaseLock(self.index)
			elif self.exception == "LockTookTooLong" or type != None:
				print "Abort: no locking possible!"


def test():
	"""
	Test for easyCache to test functionality
	"""
	eC = easyRedisCache("keyCache")

	import threading
	import time

	def worker():
		print "Worker 1 Init"
		with eC.setBlocking("key", get=True) as block:
			if block.exception == None:
				#print "Worker 1 Set"
				print block.val
				if block.val == None:
					block.val = ""
				block.val += "foo"
				time.sleep(1)

	def worker2():
		print "Worker 2 Init"
		with eC.setBlocking("key", get=True) as block:
			if block.exception == None:
				#print "Worker 2 Set"
				print block.val
				block.val += "bar"


	eC.set("key", "co")
	eC.delete("key")

	threads = []
	for i in range(5):
		t = threading.Thread(target=worker)
		threads.append(t)
		t.start()

	for i in range(5):
		t = threading.Thread(target=worker2)
		threads.append(t)
		t.start()