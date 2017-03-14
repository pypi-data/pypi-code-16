# -*- coding: utf-8 -*-

"""
Python Implements Level 2 Cache Broker
"""
import json
import os
import pickle
import sys
import threading
import uuid

import redis

from py3cache import PyInMem

if sys.version < '3':
    import ConfigParser as configparser
else:
    import configparser


class Py3Cache (threading.Thread):

    client_id = ''
    memory_cache = ''
    redis_conn = ''  # Refer to Instance of redis connection
    redis_pubsub = '' # Redis Pub/Sub Channel
    redis_channel = ''
    debug = False

    def __init__(self):
        self.client_id = uuid.uuid1().__str__()
        threading.Thread.__init__(self)
        config = configparser.ConfigParser()
        config.optionxform = str  # 保留配置文件key的大小写设定
        config_path = os.path.join(os.path.split(os.path.realpath(__file__))[0], "config.ini")
        config.read(config_path)

        self.debug = "true" == config.get("global", "debug")

        opts = config.items('memory')
        self.memory_cache = PyInMem.PyInMem(opts, callback=self.callback)

        redis_host = config.get("redis", "host")
        redis_port = config.get("redis", "port")
        redis_db = config.getint("redis", "db")
        self.redis_channel = config.get("redis", "channel")

        try:
            self.redis_conn = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
            if self.debug:
                rci = self.redis_conn.info()
                print("Connected to Redis", {"Version": rci['redis_version'], "Platform": rci['os']})

            self.redis_pubsub = self.redis_conn.pubsub()
            self.redis_pubsub.subscribe([self.redis_channel])
            self.start()

        except Exception as e:
            print("Initialize Redis Failed:", e)
            sys.exit()

    def callback(self, action, region, key=None):
        if action == 'evict':
            self.redis_conn.publish(self.redis_channel, self.__action("evict", region, key))
        elif action == 'clear':
            self.redis_conn.publish(self.redis_channel, self.__action("clear", region))
        else:
            print("Unknown callback action={0},region={1},key={2}".format(action, region, key))

    def run(self):
        for item in self.redis_pubsub.listen():
            # print(item['data'].__class__)
            if isinstance(item['data'], bytes):
                channel = item['channel'].decode()
                msg = json.loads(item['data'].decode())
                if msg['cid'] != self.client_id:
                    if self.debug:
                        print("[{0}] Message Received: {1}\n".format(channel, msg))

                    if msg['action'] == 'clear':
                        self.memory_cache._clear(msg['region'])
                    elif msg['action'] == 'evict':
                        self.memory_cache._evict(msg['region'], msg['key'])
                    elif self.debug:
                        print("Unknown message:", msg)

    def close(self):
        self.redis_pubsub.unsubscribe()

    """ Get Data From Py3Cache """
    def get(self, region, key):
        val = self.memory_cache.get(region, key)
        if val:
            return val

        redis_val = self.redis_conn.hget(region, key)
        if redis_val:
            val = pickle.loads(redis_val)

        if self.debug:
            print("Read data from redis [{0},{1}]=>{2}.".format(region, key, val))
        if val:
            self.memory_cache.set(region, key, val)
            return val

        return None

    def put(self, region, key, val):
        self.memory_cache.set(region, key, val)
        self.redis_conn.hset(region, key, pickle.dumps(val))
        ''' Broadcast evict message to all Py3Cache nodes'''
        self.redis_conn.publish(self.redis_channel, self.__action("evict", region, key))

    def evict(self, region, key):
        self.redis_conn.hdel(region, key)
        self.memory_cache.evict(region, key)
        ''' Broadcast evict message to all Py3Cache nodes'''
        self.redis_conn.publish(self.redis_channel, self.__action("evict", region, key))

    def clear(self, region):
        self.redis_conn.delete(region)
        self.memory_cache.clear(region)
        ''' Broadcast clear message to all Py3Cache nodes'''
        self.redis_conn.publish(self.redis_channel, self.__action("clear", region))

    def __action(self, action, region, key=None):
        msg = {"action": action, "region": region, "key": key, "cid": self.client_id}
        return json.dumps(msg)


if __name__ == '__main__':
    p3c = Py3Cache()

    while True:
        s_input = input("> ")
        if s_input == 'quit' or s_input == 'exit':
            break
        cmds = s_input.split()
        if cmds[0] == 'get':
            data = p3c.get(cmds[1], cmds[2])
            print('[{0},{1}] => {2}'.format(cmds[1], cmds[2], data))
        elif cmds[0] == 'set':
            p3c.put(cmds[1], cmds[2], cmds[3])
            print('[{0},{1}] <= {2}'.format(cmds[1], cmds[2], cmds[3]))
        elif cmds[0] == 'evict':
            p3c.evict(cmds[1], cmds[2])
            print('[{0},{1}] <= None'.format(cmds[1], cmds[2]))
        elif cmds[0] == 'clear':
            p3c.clear(cmds[1])
            print('[{0},*] <= None'.format(cmds[1]))
        else:
            print('Unknown command:', s_input)

    p3c.close()
    sys.exit(0)
