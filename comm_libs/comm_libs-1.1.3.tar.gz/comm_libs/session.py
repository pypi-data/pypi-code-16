# coding:utf8

"""
session 操作相关

created by : xiaochun

"""

import hashlib
import time
import memcache



class SessionClient(object):
    """
    session 操作类
    """

    def __init__(self, addr_list):
        """
        addr_list : ["127.0.0.1:11000"]
        """

        self.mem_client = memcache.Client(addr_list)


    def gen_session_key(self, client_ip, user_id):
        """
        生成session key
        """

        time_str = str(time.time())
        clock_str = str(time.clock())

        src = client_ip + str(user_id) + time_str + clock_str

        return hashlib.md5(src).hexdigest()

    def get_session(self, key):
        """
        获取session
        return : 内容
        """

        return self.mem_client.get(key)

    def set_session(self, key, value, expire=15*60):
        """
        更新session
        return : True: 成功
        """

        return self.mem_client.set(key, value, expire)

    def del_session(self, key):
        """
        删除session
        return : 非0，表示成功
        """

        return self.mem_client.delete(key)



if __name__ == "__main__":


    # 服务地址
    addr_list = ["127.0.0.1:11000"]

    session_client = SessionClient(addr_list)

    # 生成session key
    #skey = session_client.gen_session_key("127.0.0.1", "123")

    skey = "d6f731287a5babd0bbea5874d031fb76"

    print skey

    #print session_client.set_session(skey, "xxxd")

    print session_client.get_session(skey)

    #print session_client.del_session(skey)

    #print session_client.get_session(skey)






    

