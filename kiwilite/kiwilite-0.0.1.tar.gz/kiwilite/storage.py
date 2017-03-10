#-*- coding: utf-8 -*-

import io
import os
import time

BLOCK_SIZE         = 4096
BOOTSTRAP_SIZE     = BLOCK_SIZE
READER_SIZE        = 32 * BLOCK_SIZE
OFFSET_SIZE        = 8
HEADER_SIZE        = OFFSET_SIZE
INDEX_KEY_PREFIX   = 7
INDEX_KEY_SIZE     = INDEX_KEY_PREFIX + OFFSET_SIZE + OFFSET_SIZE
INDEX_MIN_SIZE     = 2 + INDEX_KEY_SIZE
INDEX_VALUE_OFFSET = 1 + INDEX_KEY_SIZE
INDEX_TIME_OFFSET  = 1 + INDEX_KEY_PREFIX
INDEX_PREV_OFFSET  = 1 + INDEX_KEY_PREFIX + OFFSET_SIZE

INDEX_KEY_BYTES     = '@ibelie'
INDEX_KEY_BYTES_ALL = chr(INDEX_KEY_SIZE) + INDEX_KEY_BYTES


class Index(object):
	__slots__ = 'offset', 'length'
	def __init__(self, offset = 0, length = 0):
		self.offset = offset
		self.length = length


MaxVarintLen = 10

def fromUint64(b):
	return ord(b[7]) | (ord(b[6]) << 8) | (ord(b[5]) << 16) | (ord(b[4]) << 24) | \
		(ord(b[3]) << 32) | (ord(b[2]) << 40) | (ord(b[1]) << 48) | (ord(b[0]) << 56)

def toUint64(x):
	return chr((x >> 56) % 256) + chr((x >> 48) % 256) + chr((x >> 40) % 256) + \
		chr((x >> 32) % 256) + chr((x >> 24) % 256) + chr((x >> 16) % 256) + \
		chr((x >> 8) % 256) + chr(x % 256)

def fromVarint(buf):
	x = s = 0
	for i in xrange(min(MaxVarintLen, len(buf))):
		b = ord(buf[i])
		if b < 0x80:
			if i > 9 or i == 9 and b > 1:
				# overflow
				return 0, -(i + 1)
			return x | b << s, i + 1
		x |= long(b & 0x7f) << s
		s += 7
	return 0, 0

def toVarint(x):
	s = ''
	while x >= 0x80:
		s += chr((x % 256) | 0x80)
		x >>= 7
	s += chr(x % 256)
	return s

def sizeVarint(x):
	n = 0
	while 1:
		n += 1
		x >>= 7
		if x == 0: break
	return n



class Storage(object):
	__slots__ = 'file', 'lasttime', 'index', 'header', 'indexOffset'

	def __init__(self, filename):
		if os.path.isfile(filename):
			self.file = open(filename, 'r+b')
		else:
			self.file = open(filename, 'w+b')
		self.lasttime = 0
		self.index = None
		self.header = 0
		self.indexOffset = 0

	def __enter__(self):
		return self

	def __exit__(self, *excinfo):
		del self

	def __del__(self):
		self.file.close()

	# Write index.
	def _writeIndex(self):
		length = 0
		for key, idx in self.index.iteritems():
			length += sizeVarint(len(key)) + len(key) + sizeVarint(idx.length) + sizeVarint(idx.offset)
		lengthStr = toVarint(length)
		length += len(lengthStr)
		self.file.write(lengthStr)

		for key, idx in self.index.iteritems():
			self.file.write(toVarint(len(key)))
			self.file.write(key)
			self.file.write(toVarint(idx.length))
			self.file.write(toVarint(idx.offset))
		return length

	# Scan the storage file and rebuild index.
	def _rebuild(self, start, end, prev = None):
		head = 0
		key = None
		buf = prev or ''
		index = {}
		anchor = 0
		if start < end:
			self.file.seek(start, io.SEEK_SET)
		while anchor < end:
			if anchor == 0:
				anchor = start
			if len(buf) <= head:
				buf = ''
			elif head != 0:
				buf = buf[head:]
			head = 0
			length = min(end - anchor, READER_SIZE - len(buf))
			if length > 0:
				buf += self.file.read(length)
				anchor += length
			elif len(buf) >= READER_SIZE:
				break
			while head < len(buf):
				if key is None:
					keyLength, keyLenSize = fromVarint(buffer(buf, head))
					if keyLenSize == 0:
						break
					elif keyLenSize < 0:
						print "[KiwiLite] Warning: ignore bad key length (%s)." \
							% repr([ord(b) for b in buf[head:head + MaxVarintLen]])
						break
					elif head + keyLenSize + keyLength > len(buf):
						if keyLength >= READER_SIZE / 2:
							length = keyLength - len(buf) + head + keyLenSize
							key = buf[head + keyLenSize:] + self.file.read(length)
							anchor += length
							head = len(buf)
						break
					else:
						head += keyLenSize
						key = buf[head: head + keyLength]
						head += keyLength

				length, lengthSize = fromVarint(buffer(buf, head))
				if lengthSize == 0:
					break
				elif lengthSize < 0:
					print "[KiwiLite] Warning: ignore bad value length (%s)." \
						% repr([ord(b) for b in buf[head:head + MaxVarintLen]])
					break
				if start == HEADER_SIZE:
					head += lengthSize
					offset = anchor + head - len(buf)
					head += length
					if head > len(buf):
						anchor += head - len(buf)
						self.file.seek(anchor, io.SEEK_SET)
				else:
					offset, offsetSize = fromVarint(buffer(buf, head + lengthSize))
					if offsetSize == 0:
						break
					elif offsetSize < 0:
						print "[KiwiLite] Warning: ignore bad offset (%s)." \
							% repr([ord(b) for b in buf[head + lengthSize:head + lengthSize + MaxVarintLen]])
						break
					head += lengthSize + offsetSize

				if len(key) != INDEX_KEY_SIZE or key[:INDEX_KEY_PREFIX] != INDEX_KEY_BYTES:
					if length <= 0 or length >= anchor:
						if key in index: del index[key]
					else:
						index[key] = Index(offset, length)
				key = None
		return index

	# Verify the storage file and refresh the cached index.
	def _verify(self):
		if not self.file or self.index is not None:
			return

		# read header and index of storage file
		self.file.seek(0, io.SEEK_SET)
		headerBytes = self.file.read(HEADER_SIZE)
		if not headerBytes or len(headerBytes) < HEADER_SIZE:
			# 1. the file has no data, init cache
			self.header = 0
			self.indexOffset = 0
			self.index = {}
			return
		header = fromUint64(headerBytes)
		if self.header == header: return

		# 2. bad index data; scan the whole file to rebuild index
		def _rebuild():
			self.file.seek(0, io.SEEK_END)
			size = self.file.tell()
			self.index = self._rebuild(HEADER_SIZE, size)
			self.header = header
			self.indexOffset = size - INDEX_VALUE_OFFSET
			print "[KiwiLite] Rebuild index."

		offset = header
		self.file.seek(offset, io.SEEK_SET)
		indexBytes = self.file.read(READER_SIZE)
		offset += len(indexBytes)

		if indexBytes[:1 + INDEX_KEY_PREFIX] != INDEX_KEY_BYTES_ALL:
			print "[KiwiLite] Warning: bad index-key-prefix (%s), rebuild index." \
				% repr([ord(b) for b in indexBytes[:1 + INDEX_KEY_PREFIX]])
			return _rebuild()
		indexLength, indexLenSize = fromVarint(buffer(indexBytes, INDEX_VALUE_OFFSET))
		if indexLenSize <= 0 or indexLength <= 0:
			print "[KiwiLite] Warning: bad index length (%s), rebuild index." \
				% repr([ord(b) for b in indexBytes[INDEX_VALUE_OFFSET:INDEX_VALUE_OFFSET + MaxVarintLen]])
			return _rebuild()
		indexBytes = indexBytes[indexLenSize + INDEX_VALUE_OFFSET:]

		# 3. refresh index
		self.index = self._rebuild(offset, offset + indexLength - indexLenSize, indexBytes)
		self.header = header
		self.indexOffset = header

	# Get value bytes of key.
	def Get(self, key):
		key = str(key)
		self._verify()
		if self.index is None or key not in self.index:
			return ""
		idx = self.index[key]
		self.file.seek(idx.offset, io.SEEK_SET)
		return self.file.read(idx.length)

	# Set map data of key and value and save storage file.
	def Set(self, data):
		self._verify()

		# verify, seek and clear old index
		if self.indexOffset == 0:
			offset = HEADER_SIZE
			self.file.seek(offset, io.SEEK_SET)
		else:
			offset = self.indexOffset + INDEX_VALUE_OFFSET
			self.file.seek(offset, io.SEEK_SET)
			self.file.write(chr(0))
			offset += 1

		# write (key, value) data
		index = {}
		for key, value in data.iteritems():
			key = str(key)
			keyLength = len(key)
			keyLenStr = toVarint(keyLength)
			self.file.write(keyLenStr)
			offset += len(keyLenStr)
			self.file.write(key)
			offset += keyLength

			value = str(value)
			valueLength = len(value)
			valueLenStr = toVarint(valueLength)
			self.file.write(valueLenStr)
			offset += len(valueLenStr)
			valueLength > 0 and self.file.write(value)
			index[key] = Index(offset, valueLength)
			offset += valueLength

		# get new index offset and write index key
		self.file.write(INDEX_KEY_BYTES_ALL)
		currtime = long(time.time() * 1e9)
		if self.lasttime >= currtime:
			self.lasttime += 1
		else:
			self.lasttime = currtime
		self.file.write(toUint64(self.lasttime))
		self.file.write(toUint64(self.indexOffset))

		# write index
		for key, idx in index.iteritems():
			if idx.length > 0:
				self.index[key] = idx
			elif key in self.index:
				del self.index[key]
		self._writeIndex()

		# write header
		self.file.seek(0, io.SEEK_SET)
		self.file.write(toUint64(offset))
		self.indexOffset = offset
		self.header = offset

	# Log: a list of timestones.
	def Log(self, start, end):
		self._verify()

		timestone = []
		offset = self.indexOffset
		while offset > 0:
			self.file.seek(offset, io.SEEK_SET)
			indexBytes = self.file.read(INDEX_MIN_SIZE)
			if (offset != self.indexOffset and indexBytes[INDEX_MIN_SIZE - 1] != '\0') or \
				indexBytes[:1 + INDEX_KEY_PREFIX] != INDEX_KEY_BYTES_ALL:
				print "[KiwiLite] Log: Index Error (%s)." % repr([ord(b) for b in indexBytes])
				break
			else:
				t = fromUint64(buffer(indexBytes, INDEX_TIME_OFFSET))
				if end == 0 or t <= end:
					timestone.append(t)
				if start != 0 and t < start:
					break
				offset = fromUint64(buffer(indexBytes, INDEX_PREV_OFFSET))
		for i in xrange(len(timestone) / 2):
			j = len(timestone) - i - 1
			timestone[i], timestone[j] = timestone[j], timestone[i]
		return timestone

	# Lighten to the first timestone after timestamp,
	# and clear all invalid data before timestamp.
	# Data will not lose, but cannot rollback before timestamp.
	def Lighten(self, timestamp):
		self._verify()
		if self.indexOffset == 0:
			print "[KiwiLite] Warning: storage file is empty."
			return False

		timestone = []
		if timestamp == 0:
			timestone.append(self.indexOffset)
			self.file.seek(self.indexOffset, io.SEEK_SET)
			indexBytes = self.file.read(INDEX_MIN_SIZE)
			if not indexBytes:
				t = long(time.time() * 1e9)
			elif indexBytes[:1 + INDEX_KEY_PREFIX] != INDEX_KEY_BYTES_ALL:
				print "[KiwiLite] Lighten: Index Error (%s)." % repr([ord(b) for b in indexBytes])
				return False
			else:
				t = fromUint64(buffer(indexBytes, INDEX_TIME_OFFSET))
		else:
			# backtracking
			pT = 0
			prev = self.indexOffset
			while prev > 0:
				self.file.seek(prev, io.SEEK_SET)
				indexBytes = self.file.read(INDEX_MIN_SIZE)
				if not indexBytes or (prev != self.indexOffset and indexBytes[INDEX_MIN_SIZE - 1] != '\0') or \
					indexBytes[:1 + INDEX_KEY_PREFIX] != INDEX_KEY_BYTES_ALL:
					print "[KiwiLite] Lighten: Index Error (%s)." % repr([ord(b) for b in indexBytes])
					return False
				pT = fromUint64(buffer(indexBytes, INDEX_TIME_OFFSET))
				if pT < timestamp:
					break
				else:
					t = pT
					timestone.append(prev)
					prev = fromUint64(buffer(indexBytes, INDEX_PREV_OFFSET))
			if prev == 0:
				print "[KiwiLite] Warning: no need to lighten, current %s." % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pT / 1e9))
				return False

		# sort timestone
		for i in xrange(len(timestone) / 2):
			j = len(timestone) - i - 1
			timestone[i], timestone[j] = timestone[j], timestone[i]
		lightenEnd = timestone[0]

		# rebuild index of timestamp
		index = self.index
		if lightenEnd != self.indexOffset:
			# scan before indexOffset to rebuild index
			index = self._rebuild(HEADER_SIZE, lightenEnd)

		# sort fragments
		fragments = {}
		for key, idx in index.iteritems():
			keyLength = len(key)
			keyLenSize = sizeVarint(keyLength)
			valueLength = idx.length
			extraLength = sizeVarint(valueLength) + keyLength + keyLenSize
			fragments[idx.offset - extraLength] = (extraLength + valueLength, keyLenSize, keyLenSize + keyLength)

		# defragmentation and update self.index
		offset = HEADER_SIZE
		for off, (length, start, end) in sorted(fragments.iteritems(), key = lambda (k, v): k):
			self.file.seek(off, io.SEEK_SET)
			data = self.file.read(length)
			self.file.seek(offset, io.SEEK_SET)
			self.file.write(data)
			offset += len(data)
			key = data[start:end]
			if key in self.index and self.index[key].offset < lightenEnd:
				self.index[key].offset = offset - self.index[key].length

		# update self.index
		deltaOffset = lightenEnd - offset
		for idx in self.index.itervalues():
			if idx.offset > lightenEnd:
				idx.offset -= deltaOffset

		# shift data
		shiftEnd = self.indexOffset + INDEX_VALUE_OFFSET
		while lightenEnd < shiftEnd:
			self.file.seek(lightenEnd, io.SEEK_SET)
			data = self.file.read(min(shiftEnd - lightenEnd, READER_SIZE))
			self.file.seek(offset, io.SEEK_SET)
			self.file.write(data)
			lightenEnd += len(data)
			offset += len(data)

		# update 'prev' field of timestone
		prevOffset = 0
		for off in timestone:
			self.file.seek(off - deltaOffset + INDEX_PREV_OFFSET, io.SEEK_SET)
			self.file.write(toUint64(prevOffset))
			prevOffset = off - deltaOffset

		# write index, header and truncate
		self.file.seek(offset, io.SEEK_SET)
		offset += self._writeIndex()
		self.file.seek(0, io.SEEK_SET)
		self.file.write(toUint64(self.indexOffset - deltaOffset))
		self.file.truncate(offset)
		self.indexOffset -= deltaOffset
		self.header = self.indexOffset

		print "[KiwiLite] Lighten file to %s." % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t / 1e9))
		return True

	# Rollback to the last timestone before timestamp,
	# and clear all data after timestamp.
	def Rollback(self, timestamp):
		self._verify()

		def _clear():
			self.file.truncate(0)
			self.header = 0
			self.indexOffset = 0
			self.index = {}
			return True

		# clear all data
		if timestamp == 0:
			print "[KiwiLite] Clear file."
			return _clear()

		# verify
		if self.indexOffset == 0:
			print "[KiwiLite] Warning: storage file is empty."
			return False

		# backtracking
		t = 0
		indexOffset = self.indexOffset
		while indexOffset > 0:
			self.file.seek(indexOffset, io.SEEK_SET)
			indexBytes = self.file.read(INDEX_MIN_SIZE)
			if not indexBytes or (indexOffset != self.indexOffset and indexBytes[INDEX_MIN_SIZE - 1] != '\0') or \
				indexBytes[:1 + INDEX_KEY_PREFIX] != INDEX_KEY_BYTES_ALL:
				print "[KiwiLite] Rollback: Index Error (%s)." % repr([ord(b) for b in indexBytes])
				return False
			t = fromUint64(buffer(indexBytes, INDEX_TIME_OFFSET))
			if t <= timestamp:
				break
			else:
				indexOffset = fromUint64(buffer(indexBytes, INDEX_PREV_OFFSET))
		if indexOffset == 0:
			print "[KiwiLite] Warning: clear file, before %s." % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t / 1e9))
			return _clear()
		elif indexOffset == self.indexOffset:
			print "[KiwiLite] Warning: no need to rollback, current %s." % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t / 1e9))
			return False

		# scan before timestamp to rebuild index
		self.index = self._rebuild(HEADER_SIZE, indexOffset)

		# write index
		size = indexOffset + INDEX_VALUE_OFFSET
		self.file.seek(size, io.SEEK_SET)
		size += self._writeIndex()

		# write header and truncate
		self.file.seek(0, io.SEEK_SET)
		self.file.write(toUint64(indexOffset))
		self.file.truncate(size)
		self.header = indexOffset
		self.indexOffset = indexOffset

		print "[KiwiLite] Rollback file to %s." % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t / 1e9))
		return True
