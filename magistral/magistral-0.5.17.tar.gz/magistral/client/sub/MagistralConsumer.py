'''
Created on 13 Aug 2016
@author: rizarse
'''
from os.path import expanduser

from kafka.consumer.group import KafkaConsumer
from kafka.structs import TopicPartition
from magistral.Message import Message
from magistral.client.MagistralException import MagistralException

class MagistralConsumer(object):
    
    __HISTORY_DATA_FETCH_SIZE_LIMIT = 10000;

    def __init__(self, pubKey, subKey, secretKey, bootstrap, token, cipher = None, uid = None):
        self.__pubKey = pubKey
        self.__subKey = subKey
        self.__secretKey = secretKey
        
        self.__token = token
        
        self.uid = uid
                
        self.__bootstrap = bootstrap.split(',')
        if cipher is not None: self.__cipher = cipher
    
    def history(self, topic, channel, records):
        
        messages = []
        
        if self.uid == None:
            self.consumer = KafkaConsumer(bootstrap_servers = self.__bootstrap,
                    check_crcs = False,
                    exclude_internal_topics = True,
                    session_timeout_ms = 10000,
                    reconnect_backoff_ms = 10000,
                    heartbeat_interval_ms = 2000,
                    retry_backoff_ms = 500,
                    fetch_min_bytes = 64,
                    fetch_max_wait_ms = 96,           
                    enable_auto_commit = False,
                    max_in_flight_requests_per_connection = 4,
                    api_version = (0, 10));
        else:            
            home = expanduser("~")
            
            self.consumer = KafkaConsumer(bootstrap_servers = self.__bootstrap,
                    check_crcs = False,
                    exclude_internal_topics = True,
                    session_timeout_ms = 10000,
                    reconnect_backoff_ms = 10000,
                    heartbeat_interval_ms = 2000,
                    retry_backoff_ms = 500,
                    fetch_min_bytes = 64,
                    fetch_max_wait_ms = 96,           
                    enable_auto_commit = False,
                    max_in_flight_requests_per_connection = 4,
                    security_protocol = 'SSL',
                    ssl_check_hostname = False,
                    ssl_keyfile = home + '/magistral/' + self.__token + '/key.pem',
                    ssl_cafile = home + '/magistral/' + self.__token + '/ca.pem',
                    ssl_certfile = home + '/magistral/' + self.__token + '/certificate.pem',
                    api_version = (0, 10));
            
        if (records > self.__HISTORY_DATA_FETCH_SIZE_LIMIT): records = self.__HISTORY_DATA_FETCH_SIZE_LIMIT;
            
        kfkTopic = self.__subKey + "." + topic;
        x = TopicPartition(kfkTopic, channel);
        
        self.consumer.assign([x]);
        self.consumer.seek_to_end();        
        last = self.consumer.position(x);
        
        pos = last - records if last > records else 0;
        self.consumer.seek(x, pos);
        
        data = self.consumer.poll(256);   
        
        endIsNotReached = True;
        while endIsNotReached:
            
            if len(data.values()) == 0:
                return messages;
            
            records = list(data.values())
            
            for record in records[0]:
                index = record[2];
                if index >= last - 1: endIsNotReached = False;
                
                message = Message(record[0][41:], record[1], record[6], index, record[3]);
                messages.append(message);
            
            if endIsNotReached == False: 
                self.consumer.close();
                return messages;
            
            pos = pos + len(messages)
            self.consumer.seek(x, pos);
            data = self.consumer.poll(256);
            
        self.consumer.close();
        
        return messages;
    
    def historyForTimePeriod(self, topic, channel, start, end, limit = -1):
        
        out = []        
        
        try:
            kfkTopic = self.__subKey + "." + topic;
            x = TopicPartition(kfkTopic, channel);
            
            if self.uid == None:
                self.consumer = KafkaConsumer(bootstrap_servers = self.__bootstrap,
                        check_crcs = False,
                        exclude_internal_topics = True,
                        session_timeout_ms = 30000,
                        reconnect_backoff_ms = 10000,
                        heartbeat_interval_ms = 2000,
                        retry_backoff_ms = 500,
                        fetch_min_bytes = 32,
                        fetch_max_wait_ms = 96,           
                        enable_auto_commit = False,
                        max_partition_fetch_bytes = 65536,
                        max_in_flight_requests_per_connection = 4,
                        api_version = (0, 10));
            else:            
                home = expanduser("~")
                
                self.consumer = KafkaConsumer(bootstrap_servers = self.__bootstrap,
                        check_crcs = False,
                        exclude_internal_topics = True,
                        session_timeout_ms = 30000,
                        reconnect_backoff_ms = 10000,
                        heartbeat_interval_ms = 2000,
                        retry_backoff_ms = 500,
                        fetch_min_bytes = 32,
                        fetch_max_wait_ms = 96,           
                        enable_auto_commit = False,
                        max_partition_fetch_bytes = 65536,
                        max_in_flight_requests_per_connection = 4,
                        security_protocol = 'SSL',
                        ssl_check_hostname = False,
                        ssl_keyfile = home + '/magistral/' + self.__token + '/key.pem',
                        ssl_cafile = home + '/magistral/' + self.__token + '/ca.pem',
                        ssl_certfile = home + '/magistral/' + self.__token + '/certificate.pem',
                        api_version = (0, 10));
                        
            self.consumer = KafkaConsumer(bootstrap_servers = self.__bootstrap);
            self.consumer.assign([x]);
            
            self.consumer.seek_to_end();        
            last = self.consumer.position(x);
        
            position = last - 1000;
            
            found = False;
            while found == False:
                self.consumer.seek(x, position);
                data = self.consumer.poll(500);
                 
                if x not in data.keys() or len(data[x]) == 0: break;
                
                record = data[x][0];
                timestamp = record[3];
 
                if timestamp < start: 
                    found = True;
                    break;
                 
                position = position - 1000;
             
            self.consumer.close();
                       
            if self.uid == None:
                self.с = KafkaConsumer(bootstrap_servers = self.__bootstrap,
                        check_crcs = False,
                        exclude_internal_topics = True,
                        session_timeout_ms = 10000,
                        reconnect_backoff_ms = 10000,
                        heartbeat_interval_ms = 2000,
                        retry_backoff_ms = 500,
                        fetch_min_bytes = 32,
                        fetch_max_wait_ms = 96,           
                        enable_auto_commit = False,
                        max_partition_fetch_bytes = 65536,
                        max_in_flight_requests_per_connection = 4,
                        api_version = (0, 10));
            else:            
                home = expanduser("~")
                
                self.с = KafkaConsumer(bootstrap_servers = self.__bootstrap,
                        check_crcs = False,
                        exclude_internal_topics = True,
                        session_timeout_ms = 10000,
                        reconnect_backoff_ms = 10000,
                        heartbeat_interval_ms = 2000,
                        retry_backoff_ms = 500,
                        fetch_min_bytes = 32,
                        fetch_max_wait_ms = 96,           
                        enable_auto_commit = False,
                        max_partition_fetch_bytes = 65536,
                        max_in_flight_requests_per_connection = 4,
                        security_protocol = 'SSL',
                        ssl_check_hostname = False,
                        ssl_keyfile = home + '/magistral/' + self.__token + '/key.pem',
                        ssl_cafile = home + '/magistral/' + self.__token + '/ca.pem',
                        ssl_certfile = home + '/magistral/' + self.__token + '/certificate.pem',
                        api_version = (0, 10));  
                      
            self.с.assign([x]);
                       
            self.c.seek(x, position);                        
            data = self.с.poll(256);
            
            while (x in data.keys() and len(data[x]) > 0):
                
                for record in data[x] :
                    timestamp = record[3];
                    if timestamp < start: continue;
                    
                    index = record[2];
                    
                    if timestamp > end or index >= last - 1:  
                        self.с.close();                 
                        return out;
                                    
                    message = Message(record[0][41:], record[1], record[6], index, timestamp);
                    out.append(message); 
                    
                    if limit is not None and limit > 0 and len(out) >= limit:
                        self.с.close();                 
                        return out;                 
                    
                self.с.seek(x, position + len(data[x]));                        
                data = self.с.poll(256);
            
            return out;
        
        except:
            
            raise MagistralException("Exception during history invocation occurred");
