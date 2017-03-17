'''
Created on 8 Dec 2016
@author: rizarse
'''

import threading

from os.path import expanduser
from kafka.producer.kafka import KafkaProducer
import time

class Producer(threading.Thread):
    
    def __init__(self, setting, uid, token):
        threading.Thread.__init__(self)
        
        home = expanduser("~")
         
        self.p = KafkaProducer(bootstrap_servers = setting["bootstrap_servers"],
                                    client_id = token,
                                    compression_type = setting["compression_type"],
                                    value_serializer = setting["value_serializer"],
                                    key_serializer = setting["key_serializer"],
                                    security_protocol = 'SSL',
                                    ssl_check_hostname = False,
                                    ssl_keyfile = home + '/magistral/' + token + '/key.pem',
                                    ssl_cafile = home + '/magistral/' + token + '/ca.pem',
                                    ssl_certfile = home + '/magistral/' + token + '/certificate.pem', 
                                    linger_ms = setting["linger_ms"],
                                    retries = setting["retries"],
                                    reconnect_backoff_ms = 1000,
                                    api_version = (0, 10),
                                    partitioner = None,
                                    acks = 0);  
                                    
        self.__isAlive = True
        
    def publish(self, topic, value, key, partition):
        return self.p.send(topic, value, key, partition)
        
    def run(self):
        
        threadLock.acquire(False)
        
        while self.__isAlive:
            try:
                time.sleep(0.1)                    
            except:
                pass
              
        threadLock.release()
        self.p.close(2)
        
    def close(self):
        self.__isAlive = False
    
threadLock = threading.Lock()  