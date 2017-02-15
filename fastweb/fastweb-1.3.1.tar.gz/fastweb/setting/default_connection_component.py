# coding:utf8


from fastweb.component.db.mysql import (SyncMysql, AsynMysql)
from fastweb.component.db.rds import (AsynRedis, SyncRedis)
from fastweb.component.db.mongo import (AsynMongo, SyncMongo)
from fastweb.component.rpc.tft import (AsynRpc, SyncRpc)


# 默认连接池大小
DEFAULT_POOL_SIZE = 60

# 同步组件
SYNC_CONN_COMPONENTS = [('mysql', SyncMysql, DEFAULT_POOL_SIZE),
                        ('redis', SyncRedis, DEFAULT_POOL_SIZE),
                        ('mongo', SyncMongo, DEFAULT_POOL_SIZE),
                        ('rpc', SyncRpc, DEFAULT_POOL_SIZE)]

# 异步组件
ASYN_CONN_COMPONENTS = [('mysql', AsynMysql, DEFAULT_POOL_SIZE),
                        ('redis', AsynRedis, DEFAULT_POOL_SIZE),
                        ('mongo', AsynMongo, DEFAULT_POOL_SIZE),
                        ('rpc', AsynRpc, DEFAULT_POOL_SIZE)]

