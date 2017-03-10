#-*- coding: utf-8 -*-

import random
data = None
testpath = 'kiwilite_storage_test'

def setup():
	global data
	if data is None:
		data = [{str(i): ''.join([chr(random.randint(0, 255)) for _ in xrange(random.randint(0, 512))]) for i in random.sample(xrange(2000), 1000)} for _ in xrange(10)]
	import os
	import shutil
	if os.path.isdir(testpath):
		shutil.rmtree(testpath)
	os.mkdir(testpath)

def teardown():
	import shutil
	shutil.rmtree(testpath)

def _getset(Storage, suffix):
	path = '%s/getset_%s' % (testpath, suffix)
	print path
	with Storage(path) as storage:
		for d in data:
			storage.Set(d)
			for k, v1 in d.iteritems():
				v2 = storage.Get(k)
				assert v1 == v2, 'Get error: %s %d %d %s %s' % (k, len(v1), len(v2), [ord(b) for b in v1[:10]], [ord(b) for b in v2[:10]])
	print '[Test] GetSet: Single storage instance test ok.'

	for d in data:
		with Storage(path) as storage:
			storage.Set(d)
		with Storage(path) as storage:
			for k, v1 in d.iteritems():
				v2 = storage.Get(k)
				assert v1 == v2, 'Get error: %s %d %d %s %s' % (k, len(v1), len(v2), [ord(b) for b in v1[:10]], [ord(b) for b in v2[:10]])
	print '[Test] GetSet: Multiple storage instance test ok.'

def test_getset_python():
	from storage import Storage
	_getset(Storage, 'python')

def test_getset_c():
	from _storage import Storage
	_getset(Storage, 'c')

def _lighten(Storage, suffix):
	path = '%s/lighten_%s' % (testpath, suffix)
	print path
	testcase = (
		lambda t: ((t[0], -1), (0, -1), (t[-1], -1)),
		lambda t: ((t[0] - 100, -1), (t[1], -1), (t[1], 1)),
		lambda t: (((t[1] + t[2]) / 2, -1), (t[3], -1), (t[5], -1), ((t[7] + t[8]) / 2, -1), (t[8], 8)),
	)

	with Storage(path) as storage:
		for i, tc in enumerate(testcase):
			for d in data:
				storage.Set(d)
			timestamp = storage.Log(0, 0)
			tc = tc(timestamp)
			for j, (timestamp, idx) in enumerate(tc):
				if j == len(tc) - 1:
					storage.Rollback(timestamp)
				else:
					storage.Lighten(timestamp)
				for k, v1 in data[idx].iteritems():
					v2 = storage.Get(k)
					assert v1 == v2, 'Get error: %d %d %s %d %d %s %s' % (i, j, k, len(v1), len(v2), [ord(b) for b in v1[:10]], [ord(b) for b in v2[:10]])
			storage.Rollback(0)
	print '[Test] Lighten: Single storage instance test ok.'

	for i, tc in enumerate(testcase):
		with Storage(path) as storage:
			for d in data:
				storage.Set(d)
			timestamp = storage.Log(0, 0)
			tc = tc(timestamp)
		for j, (timestamp, idx) in enumerate(tc):
			with Storage(path) as storage:
				if j == len(tc) - 1:
					storage.Rollback(timestamp)
				else:
					storage.Lighten(timestamp)
			with Storage(path) as storage:
				for k, v1 in data[idx].iteritems():
					v2 = storage.Get(k)
					assert v1 == v2, 'Get error: %d %d %s %d %d %s %s' % (i, j, k, len(v1), len(v2), [ord(b) for b in v1[:10]], [ord(b) for b in v2[:10]])
		with Storage(path) as storage:
			storage.Rollback(0)
	print '[Test] Lighten: Multiple storage instance test ok.'

def test_lighten_python():
	from storage import Storage
	_lighten(Storage, 'python')

def test_lighten_c():
	from _storage import Storage
	_lighten(Storage, 'c')

def _rollback(Storage, suffix):
	EMPTY_INDEX = 9527
	path = '%s/rollback_%s' % (testpath, suffix)
	print path
	testcase = (
		lambda t: ((t[-1], -1), (t[-1] + 100, -1), ((t[-1] + t[-2]) / 2, -2), (t[-3], -3), (t[-5], -5), ((t[-7] + t[-8]) / 2, -8), (t[0] - 100, EMPTY_INDEX), (0, EMPTY_INDEX)),
	)
	with Storage(path) as storage:
		for i, tc in enumerate(testcase):
			for d in data:
				storage.Set(d)
			timestamp = storage.Log(0, 0)
			tc = tc(timestamp)
			for j, (timestamp, idx) in enumerate(tc):
				storage.Rollback(timestamp)
				if idx == EMPTY_INDEX:
					for d in data:
						for k in d:
							v = storage.Get(k)
							assert not v, "Get not None: %d %d %s %d %s" % (i, j, k, len(v), [ord(b) for b in v[:10]])
				else:
					for k, v1 in data[idx].iteritems():
						v2 = storage.Get(k)
						assert v1 == v2, 'Get error: %d %d %s %d %d %s %s' % (i, j, k, len(v1), len(v2), [ord(b) for b in v1[:10]], [ord(b) for b in v2[:10]])
	print '[Test] Rollback: Single storage instance test ok.'

	for i, tc in enumerate(testcase):
		with Storage(path) as storage:
			for d in data:
				storage.Set(d)
			timestamp = storage.Log(0, 0)
			tc = tc(timestamp)
		for j, (timestamp, idx) in enumerate(tc):
			with Storage(path) as storage:
				storage.Rollback(timestamp)
			with Storage(path) as storage:
				if idx == EMPTY_INDEX:
					for d in data:
						for k in d:
							v = storage.Get(k)
							assert not v, "Get not None: %d %d %s %d %s" % (i, j, k, len(v), [ord(b) for b in v[:10]])
				else:
					for k, v1 in data[idx].iteritems():
						v2 = storage.Get(k)
						assert v1 == v2, 'Get error: %d %d %s %d %d %s %s' % (i, j, k, len(v1), len(v2), [ord(b) for b in v1[:10]], [ord(b) for b in v2[:10]])
	print '[Test] Rollback: Multiple storage instance test ok.'

def test_rollback_python():
	from storage import Storage
	_rollback(Storage, 'python')

def test_rollback_c():
	from _storage import Storage
	_rollback(Storage, 'c')
