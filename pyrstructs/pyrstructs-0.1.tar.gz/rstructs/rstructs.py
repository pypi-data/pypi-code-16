#!/usr/bin/env python
"""
A simple collection of data structures backed by Redis
We try to act as a replacement for python built-in datatypes by mimicing the built in functions

Examples

from redis import StrictRedis
from rstructs import rStruct
sr = StrictRedis(host="192.168.1.101", port=6379, db=0)
r = rStruct(sr)

# List examples
l_1 = r.list([1,2,3])
l_2 = r.list([4,5,6])
l_1.extend(l_2)
>> ['1', '2', '3', '4', '5', '6']

# Set examples
s_1 = r.set([i for i in xrange(0,10)])
s_2 = r.set([i for i in xrange(-5, 6)])
s_3 = r.set([i for i in xrange(4, 15)])
s_4 = r.set([i for i in xrange(4, 8)])
s_5 = r.set([i for i in xrange(15, 20)])
s_empty = r.set([])

s_1 & s_2 & s_3
>> set(['5', '4'])
s_1 | s_2 | s_3
>> set(['11', '1', '13', '12', '7', '14', '0', '6', '10', '-5',
       '-4', '3', '2', '-1', '4', '-3', '-2', '9', '5', '8'])
s_1.isdisjoint(s_2)
>> False
s_1.isdisjoint(s_5)
>> True
s_5 |= s_4
print s_5
>> set(['15', '17', '16', '19', '18', '5', '4', '7', '6'])

# Dict examples

# To remove them all
from structs import delete_all_temp_objects
delete_all_temp_objects(sr)

"""
from datetime import datetime
from hashlib import md5

class rStruct(object):
    def __init__(self, REDIS_CONNECTION=None):
        self.r = REDIS_CONNECTION

    def list(self, iterable=None, REDIS_KEY=None, replace=False):
        return rList(iterable=iterable, REDIS_CONNECTION=self.r, REDIS_KEY=REDIS_KEY, replace=replace)

    def set(self, iterable=None, REDIS_KEY=None, replace=False):
        return rSet(iterable=iterable, REDIS_CONNECTION=self.r, REDIS_KEY=REDIS_KEY, replace=replace)

    def dict(self, REDIS_KEY=None, replace=False):
        return rDict(REDIS_CONNECTION=self.r, REDIS_KEY=REDIS_KEY, replace=replace)


class rList(list):
    def __init__(self, iterable=None, REDIS_CONNECTION=None, REDIS_KEY=None, replace=False, *args, **kwargs):
        if REDIS_CONNECTION is None:
            raise Exception("no REDIS_CONNECTION specified")
        if REDIS_KEY is None:
            REDIS_KEY = get_temp_name(self.__module__, self.__class__.__name__)
        self.r = REDIS_CONNECTION
        self.r_key = REDIS_KEY
        if iterable is not None:
            if replace:
                self.r.delete(self.r_key)
            self.extend(iterable)
        super(list, self).__init__(*args, **kwargs)

    def get_name(self):
        return self.r_key

    def __len__(self):
        return self.r.llen(self.r_key)

    def __getitem__(self, key):
        return self.r.lindex(self.r_key, key)

    def __setitem__(self, key, value):
        return self.r.lset(self.r_key, key, value)

    def __delitem__(self, key):
        return self.r.eval(LuaScripts.LREMINDEX, 1, self.r_key, key)

    def __iter__(self) :
        for x in self.r.lrange(self.r_key, 0, -1):
            yield x

    def __reversed__(self):
        for x in reversed(self.r.lrange(self.r_key, 0, -1)):
            yield x

    def __contains__(self, item):
        if self._index(item) >= 0:
            return True
        return False

    def __getslice__(self, i, j):
        return self.r.lrange(self.r_key, i, j-1)

    def __delslice__(self, i, j):
        if j >= len(self):
            j = -1
        return self.r.eval(LuaScripts.LREMINDEXSLICE, 1, self.r_key, i, j)

    def append(self, object):
        return self.r.rpush(self.r_key, object)

    def count(self):
        return self.r.llen(self.r.key)

    def extend(self, iterable):
        p = self.r.pipeline()
        for item in iterable:
            p.rpush(self.r_key, item)
        p.execute()

    def _index(self, value):
        return self.r.eval(LuaScripts.LGET_INDEX, 1, self.r_key, value)

    def index(self, value, start, stop):
        return NotImplemented

    def insert(self, index, object):
        return self.r.linsert(self.r_key, "before", self.r.lindex(self.r_key, index), object)

    def pop(self, index):
        value = self.r.lindex(self.r_key, index)
        del self[index]
        return value

    def rpop(self):
        return self.r.rpop(self.r_key)

    def lpop(self):
        return self.r.lpop(self.r_key)

    def ltrim(self, start, stop):
        return self.r.ltrim(self.r_key, start, stop)

    def lrange(self, start, stop):
        return self.r.lrange(self.r_key, start, stop)

    def remove(self, value):
        return self.r.lrem(self.r_key, 0, value)

    def reverse(self):
        return self.r.eval(LuaScripts.LREVERSE, 1, self.r_key)

    def sort(self, cmp=None, key=None, reverse=False):
        pass

    def __str__(self):
        return repr(self)

    def __unicode__(self):
        return repr(self)


class rSet(set):
    def __init__(self, iterable=None, REDIS_CONNECTION=None, REDIS_KEY=None, replace=False, *args, **kwargs):
        if REDIS_CONNECTION is None:
            raise Exception("no REDIS_CONNECTION specified")
        if REDIS_KEY is None:
            REDIS_KEY = get_temp_name(self.__module__, self.__class__.__name__)
        self.r = REDIS_CONNECTION
        self.r_key = REDIS_KEY
        if iterable is not None:
            if replace:
                self.r.delete(self.r_key)
            if len(iterable) > 0:
                self.r.sadd(self.r_key, *iterable)
        super(set, self).__init__(*args, **kwargs)

    def get_name(self):
        return self.r_key

    def __len__(self):
        return self.r.scard(self.r_key)

    def __iter__(self) :
        for x in self.r.smembers(self.r_key):
            yield x

    def __contains__(self, item):
        return self.r.sismember(self.r_key, item)

    def isdisjoint(self, other):
        key = get_temp_name(self.__module__, self.__class__.__name__)
        num_elements = self.intersection_store(key, *[other])
        r_value = True
        if num_elements > 0:
            r_value = False
        self.r.delete(key)
        return r_value

    def issubset(self, other):
        """ set <= other """
        key = get_temp_name(self.__module__, self.__class__.__name__)
        num_members = len(self)
        num_elements = self.intersection_store(key, *[other])
        r_value = True
        if num_elements != num_members:
            r_value = False
        self.r.delete(key)
        return r_value

    def __le__(self, other):
        return self.issubset(other)

    def __lt__(self, other):
        r_value = self.issubset(other)
        if r_value is True and len(self) != len(other):
            return True
        return False

    def issuperset(self, other):
        """ set >= other """
        if not isinstance(other, rSet):
            raise Exception("not a valid type")
        key = get_temp_name(self.__module__, self.__class__.__name__)
        num_members = len(other)
        num_elements = other.intersection_store(key, *[self])
        r_value = True
        if num_elements != num_members:
            r_value = False
        self.r.delete(key)
        return r_value

    def __ge__(self, other):
        return self.issuperset(other)

    def __gt__(self, other):
        r_value = self.issuperset(other)
        if r_value is True and len(other) != len(self):
            return True
        return False

    def union(self, *others):
        """ set | other | ... """
        return self.r.sunion(self.r_key, *[o.r_key for o in others])

    def __or__(self, other):
        return self.union(*[other])

    def __ror__(self, other):
        if isinstance(other, rSet):
            return other | self
        tmp_rset = rSet(other, self.r)
        val = tmp_rset | self
        tmp_rset.clear()
        return val

    def union_store(self, key, *others):
        return self.r.sunionstore(key, self.r_key, *[o.r_key for o in others])

    def intersection(self, *others):
        """ set & other & ... """
        return self.r.sinter(self.r_key, *[o.r_key for o in others])

    def __and__(self, other):
        return self.intersection(*[other])

    def __rand__(self, other):
        if isinstance(other, rSet):
            return other & self
        tmp_rset = rSet(other, self.r)
        val = tmp_rset & self
        tmp_rset.clear()
        return val

    def intersection_store(self, key, *others):
        return self.r.sinterstore(key, self.r_key, *[o.r_key for o in others])

    def difference(self, *others):
        """ set - other - ... """
        return self.r.sdiff(self.r_key, *[o.r_key for o in others])

    def __sub__(self, other):
        self.difference(*[other])
        return self

    def __rsub__(self, other):
        if isinstance(other, rSet):
            return other - self
        tmp_rset = rSet(other, self.r)
        val = tmp_rset - self
        tmp_rset.clear()
        return val

    def difference_store(self, key, *others):
        return self.r.sdiffstore(key, self.r_key, *[o.r_key for o in others])

    def symmetric_difference(self, other):
        """ set ^ other """
        return NotImplemented

    def __xor__(self, other):
        return self.symmetric_difference(other)

    def copy(self):
        return self.r.smembers(self.r_key)

    def update(self, *others):
        """ set |= other | ... """
        return self.r.sunion(self.r_key, *[o.r_key for o in others])

    def __ior__(self, other):
        return self.update(*[other])

    def intersection_update(self, *others):
        """ set &= other & ... """
        return self.r.sinterstore(self.r_key, self.r_key, *[o.r_key for o in others])

    def __iand__(self, other):
        self.intersection_update(*[other])
        return self

    def difference_update(self, *others):
        """ set -= other | ...  """
        return self.sdiffstore(self.r_key, slef.r_key, *[o.r_key for o in others])

    def __isub__(self, other):
        self.difference_update(*[other])
        return self

    def symmetric_difference_update(self, other):
        """ set ^= other """
        return NotImplemented

    def __ixor__(self, a, b):
        return NotImplemented

    def add(self, elem):
        self.r.sadd(self.r_key, elem)
        return self

    def remove(self, elem):
        val = self.r.srem(self.r_key, elem)
        if val == 0:
            raise KeyError
        return val

    def discard(self, elem):
        self.r.srem(self.r_key, elem)
        return self

    def pop(self):
        return self.r.spop(self.r_key)

    def clear(self):
        self.r.delete(self.r_key)
        return self


class rDict(dict):
    def __init__(self, REDIS_CONNECTION=None, REDIS_KEY=None, replace=False, *args, **kwargs):
        if REDIS_CONNECTION is None:
            raise Exception("no REDIS_CONNECTION specified")
        if REDIS_KEY is None:
            REDIS_KEY = get_temp_name(self.__module__, self.__class__.__name__)
        self.r = REDIS_CONNECTION
        self.r_key = REDIS_KEY
        super(dict, self).__init__(*args, **kwargs)

    def get_name(self):
        return self.r_key

    def __len__(self):
        return self.r.hlen(self.r_key)

    def __contains__(self, item):
        return self.r.hexists(self.r_key, item)

    def __iter__(self):
        for k in self.r.hkeys(self.r_key):
            yield k

    def __setitem__(self, key, item):
        return self.r.hset(self.r_key, key, item)

    def __delitem__(self, item):
        return self.r.hdel(self.r_key, item)

    def __getitem__(self, item):
        return self.r.hget(self.r_key, item)

    def clear(self):
        return self.r.delete(self.r_key)

    def copy(self):
        return self.r.hgetall(self.r_key)

    def fromkeys(self, seq, value):
        return NotImplemented

    def get(self, key, default=None):
        retvalue = self.r.hget(self.r_key, key)
        if retvalue is None:
            return default
        return retvalue

    def has_key(self, key):
        return self.r.hexists(self.r_key, key)

    def items(self):
        return self.r.hgetall(self.r_key).items()

    def iteritems(self):
        for k in self.r.hkeys(self.r_key):
            yield (k, self.r.hget(self.r_key, k))

    def iterkeys(self):
        for k in self.r.hkeys(self.r_key):
            yield k

    def itervalues(self):
        for v in self.r.hvalues(self.r_key):
            yield v

    def keys(self):
        return self.r.hkeys(self.r_key)

    def pop(self, key, default=None):
        retvalue = self.r.hget(self.r_key, key)
        if retvalue is None:
            if default is None:
                raise KeyError
            return default
        return retvalue

    def popitem(self):
        return NotImplemented

    def setdefault(self, key, default=None):
        retvalue = self.r.hget(self.r_key, key)
        if retvalue is None:
            self.r.hset(self.r_key, key, default)
            return default
        return retvalue

    def update(self, *others):
        for other in others:
            for k, v in other.items():
                self[k] = v
        return None

    def values(self):
        return self.r.hvalues(self.r_key)

    def viewitems(self):
        return NotImplemented

    def viewkeys(self):
        return NotImplemented

    def viewvalues(self):
        return NotImplemented


class LuaScripts(object):
    """
        This is just to prevent polluting the default namespace
    """
    LREMINDEX_COPY = """
        -- remove by index
        local TEMP_KEY = "__" .. KEYS[1];
        redis.call('del', TEMP_KEY);
        local argv1_num = tonumber(ARGV[1]);
        local r = redis.call('lrange', KEYS[1], 0, argv1_num-1);
        redis.call('rpush', TEMP_KEY, unpack(r));
        local r = redis.call('lrange', KEYS[1], argv1_num+1, -1);
        redis.call('rpush', TEMP_KEY, unpack(r));
        redis.call('rename', TEMP_KEY, KEYS[1])
        return 1
    """
    LREMINDEX = LREMINDEX_COPY
    LREMINDEXSLICE = """
        -- remove by index slicing
        local TEMP_KEY = "__" .. KEYS[1];
        redis.call('del', TEMP_KEY);
        local argv1_num = tonumber(ARGV[1]);
        local argv2_num = tonumber(ARGV[2]);
        if argv1_num > 0 then
            local r = redis.call('lrange', KEYS[1], 0, argv1_num-1);
            redis.call('rpush', TEMP_KEY, unpack(r));
        end
        if argv2_num ~= -1 then
            local r = redis.call('lrange', KEYS[1], argv2_num+1, -1);
            redis.call('rpush', TEMP_KEY, unpack(r));
        end
        redis.call('del', KEYS[1])
        redis.call('rename', TEMP_KEY, KEYS[1])
        return 1
    """
    LGET_INDEX = """
        -- get index by value,
        -- stolen from http://stackoverflow.com/questions/8899111/get-the-index-of-an-item-by-value-in-a-redis-list
        local val = ARGV[1]
        local items = redis.call('lrange', KEYS[1], 0, -1)
        for i=1,#items do
            if items[i] == val then
                return i - 1;
            end
        end
        return -1;
    """
    LREVERSE = """
        -- reverse list
        local TEMP_KEY = "__" .. KEYS[1];
        local num_items = redis.call('llen', KEYS[1])
        for i=1,num_items do
            local val = redis.call('rpop', KEYS[1]);
            redis.call('rpush', TEMP_KEY, val);
        end
        redis.call('del', KEYS[1])
        redis.call('rename', TEMP_KEY, KEYS[1])
        return 1;
    """


def get_temp_name(PREFIX="-", SUFFIX="-"):
    # all temp names will be prefix-ed by TEMP
    val = md5(str(datetime.now())).hexdigest()
    return "TEMP:RSTRUCTS:%s:%s:%s" % (PREFIX, val, SUFFIX)

def delete_all_temp_objects(REDIS_CONNECTION=None):
    if REDIS_CONNECTION is None:
        return
    REDIS_CONNECTION.delete(REDIS_CONNECTION.keys("TEMP:RSTRUCTS:*"))

if __name__ == "__main__":
    pass
