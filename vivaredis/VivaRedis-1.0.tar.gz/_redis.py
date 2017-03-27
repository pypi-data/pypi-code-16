import redis
class RedisC:
    r = None
    def __init__(self):
        #     pool = redis.ConnectionPool(host='192.168.129.117', port=6379,password = 'video_2017') 
            pool = redis.ConnectionPool(host='192.168.2.10', port=6379) 
            self.r = redis.Redis(connection_pool=pool)
    def _redis_(self):
        return self.r
