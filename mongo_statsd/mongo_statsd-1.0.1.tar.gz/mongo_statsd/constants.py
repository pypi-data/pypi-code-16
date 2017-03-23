# -*- coding: utf-8 -*-

"""
insert  query update delete getmore command flushes mapped  vsize    res non-mapped faults            locked db idx miss %     qr|qw   ar|aw  netIn netOut  conn       time
132     *0     *0     *0       0   184|0       0  1181g  2368g  7.38g      1187g      2 texas_statistic:0.8%          0       0|0     0|0    53k    23k  1060   10:17:56


inserts  	- # of inserts per second (* means replicated op)
query    	- # of queries per second
update   	- # of updates per second
delete   	- # of deletes per second
getmore  	- # of get mores (cursor batch) per second
command  	- # of commands per second, on a slave its local|replicated
flushes  	- # of fsync flushes per second
mapped   	- amount of data mmaped (total data size) megabytes
vsize    	- virtual size of process in megabytes
res      	- resident size of process in megabytes
faults   	- # of pages faults per sec
locked   	- name of and percent time for most locked database
idx miss 	- percent of btree page misses (sampled)
qr|qw    	- queue lengths for clients waiting (read|write)
ar|aw    	- active clients (read|write)
netIn    	- network traffic in - bits
netOut   	- network traffic out - bits
conn     	- number of open connections
set      	- replica set name
repl     	- replication type
                PRI - primary (master)
                SEC - secondary
                REC - recovering
                UNK - unknown
                SLV - slave
                RTR - mongos process ("router")
"""

PREFIX = 'mongo'


def safe_int(src):
    try:
        return int(src)
    except:
        return 0


def safe_tuple(src):
    """
    返回数组
    :param src:
    :return:
    """
    try:
        return [safe_int(it) for it in src.split('|')]
    except:
        return 0


def human_to_number(src):
    """
    将给人类读的，变成机器
    :param src:
    :return:
    """

    # 倍数配置
    multiple_dict = dict(
        k=1,
        m=2,
        g=3,
        t=4,
    )

    for key, multiple in multiple_dict.items():
        if key in src:
            return float(src.replace(key, '')) * (1024 ** multiple)

HEADER_LIST = [
    ('insert', 'i', safe_int),
    ('query', 'i', safe_int),
    ('update', 'i', safe_int),
    ('delete', 'i', safe_int),
    ('getmore', 'i', safe_int),
    ('command', 'i', safe_tuple),  # 返回了数组
    ('flushes', 'i', safe_int),
    ('mapped', 'g', human_to_number),
    ('vsize', 'g', human_to_number),
    ('res', 'g', human_to_number),
    ('non-mapped', 'g', human_to_number),
    ('faults', 'i', safe_int),
    ('locked db', None, None),
    ('idx miss %', None, None),
    ('qr|qw', 'i', safe_tuple),
    ('ar|aw', 'i', safe_tuple),
    ('netIn', 'i', safe_int),
    ('netOut', 'i', safe_int),
    ('conn', 'g', safe_int),
    ('time', None, None),
]

HEADER_DICT = dict([(header[0], header) for header in HEADER_LIST])

CMD_TPL = 'mongostat --quiet --noheaders -n 1'
