'''
Copyright (c) 2016, nodewire.org
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. All advertising materials mentioning features or use of this software
   must display the following acknowledgement:
   This product includes software developed by nodewire.org.
4. Neither the name of nodewire.org nor the
   names of its contributors may be used to endorse or promote products
   derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY nodewire.org ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL nodewire.org BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
import time, threading
from socket import *
import requests
from nodewire.splitter import split, getsender, getnode

import paho.mqtt.client as paho

from nodewire.tcpclient import TCPClient


class IoTComm:
    def __init__(self, account=None, password=None, process=None):
        self.publishmqtt = False
        if password and account:
            with requests.Session() as s:
                res = s.post('http://45.55.150.77:5001/login', data = {'email':account, 'pw':password})
                if res.url != u'http://45.55.150.77:5001/login':
                    r = s.get('http://45.55.150.77:5001/config').json()
                    self.instancename = str(r['instance'])
                    self.mqttbroker = str(r['broker'])
                    self.publishmqtt = True
        self.nodes = []  # list of all nodes on the network
        self.CP = None
        self.process = process
        self.address = 'remote'
        self.client = None

        self.namedports = ['temperature', 'pressure']
        self.on_connected = None
        self.debug = False

        threading.Thread(target=self.messageloop).start()


    def startMqttListener(self):
        '''
        mqtt_client = paho.Client()
        mqtt_client.connect(self.mqttbroker)
        mqtt_client.publish(self.instancename + '/node/' + self.address + '/routing', "node/" + self.address, 0,1)
        '''
        threading.Thread(target=self.mqtt_loop).start()

    def isnumber(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    def getrouter(self, node):
        list = filter(lambda n: n['node'] == node, self.nodes)
        router = self.instancename + '/cp/' + node;
        if len(list) != 0 and 'router' in list[0].keys():
            router = self.instancename + '/' + list[0]['router']
        return router

    def plaintalk2mqtt(self, msg): #outgoing
        words = split(msg)
        address = words[0]
        command = words[1]
        params = words[2:-1]
        sender = words[-1]
        router = 'node/'+self.address
        target =  self.getrouter(address)
        message = None


        if address != self.address:
            topic = self.instancename + '/' + router
            if command == 'portvalue' and sender==self.address:
                topic+='/ports/'+params[0]
                message = params[1]
            elif command == 'setportvalue':
                topic = target+'/ports/'+params[0] + '/input'
                message = params[1]
            elif command == 'getnoports':
                topic = target+'/noports/read'
            elif command == 'RoutingVia':
                topic = target + '/routing'
                message = params[1]
            elif command == 'ports' and self.ports:
                topic += '/portslist'
                message = ' '.join(p for p in self.ports)
            elif command == 'getrouter':
                pass
            else:
                if self.debug:print('plain2mq:'+msg)
                if command in self.namedports:
                    topic+='/'+ command
                    message = params[0]
            return topic, message
        else:
            if self.debug:print('plain2mq error: cant send message to self')
            return None, None

    def mqtt2plaintalk(self, topic, msg=''): #incoming
            #try:
            words = topic.split('/')
            node = words[2]
            if len(words)>3:
                command = words[3]
            else:
                command = None

            message = None
            #if node == self.address:

            if self.debug:print (words)
            if command == 'ports' and len(words)==6 and words[-1]=='input' and node==self.address:
                message = node + ' setportvalue ' + words[4] + ' ' + msg + ' remote'
            elif command == 'port' and len(words)==6 and words[-1]=='input' and node==self.address:
                message = node + ' set' + words[4] + ' ' + msg + ' remote'
            elif command == 'ports' and len(words)==5:
                message =  'remote portvalue ' + words[4] + ' ' + msg + ' ' + node
            elif command == 'send':
                message = node + ' send ' + msg + ' remote'
            elif command == 'portslist':
                message = 'remote ports ' + msg + ' ' + node
            elif len(words) == 3 and msg and node!=self.address:
                route = msg.split()
                if len(route) == 2 and route[0]=='RoutingVia':
                    message = self.address + ' mqttregister ' + node + ' ' + route[1] + ' ' + node
            elif node != self.address and command and msg and node:
                message = self.address + ' ' + command + ' ' + msg + ' ' + node
            else:
                if self.debug:print('mq2plain:' + topic)
            return message
            '''
            except Exception as ex:
                print('mq2plain error:' + str(ex))
                print(topic)
                return None
            '''
    def send(self, Node, Command, *Params):
        if self.CP:
            self.sendTCP(Node, Command, *Params)
            if self.publishmqtt:
                self.sendMQTT(Node, Command, *Params)
        else:
            self.sendMQTT(Node, Command, *Params)

    def sendTCP(self, Node, Command, *Params):
        if self.client:
            try:
                cmd = Node + ' ' + Command + ' ' + ' '.join(param for param in Params) + (' ' + self.address if len(Params) != 0 else self.address)
                if self.debug:print(cmd)
                #thread.start_new_thread(self.client.receive, (1000,))
                self.client.send(cmd+'\r\n')

            except Exception as ex:
                self.CP = None
                self.client = None
                threading.Thread(target=self.messageloop).start()
                if self.debug:print('failed to send command over LAN')
        else:
            if self.debug:print('starting TCP communication')
            self.client = TCPClient(serverHost=self.CP)
            self.client.connect()
            if self.ProcessCommand:
                self.client.received = self.ProcessCommand
                threading.Thread(target=self.client.receive, args=(1000,)).start()
            try:
                cmd = Node + ' ' + Command + ' ' + ' '.join(param for param in Params) + (' ' + self.address if len(Params) != 0 else self.address)
                if self.debug:print(cmd)
                self.client.send(cmd)
            except:
                self.CP = None
                self.client = None
                threading.Thread(target=self.messageloop).start()
                if self.debug:print('failed to send command over TCP')

    def MQTTSEND(self, cmd):
        try:
            #todo use persistent connection
            #print('MQTTSEND:'+cmd)
            topic, message = self.plaintalk2mqtt(cmd)
            if message:
                if self.debug:print('mqttsend => ' + topic + ':' + message)
                mqtt_client = paho.Client()
                mqtt_client.connect(self.mqttbroker)
                mqtt_client.publish(topic, message, 1)
            elif topic:
                if self.debug:print('what?' + topic + ':')
                mqtt_client = paho.Client()
                mqtt_client.connect(self.mqttbroker)
                mqtt_client.publish(topic,'', 1) # all topics
        except Exception as ex:
            if self.debug:print('No Network Connection:' + str(ex))

    def sendMQTT(self, Node, Command, *Params):
        cmd = Node + ' ' + Command + ' ' + ' '.join(param for param in Params) + (' ' + self.address if len(Params) != 0 else self.address)
        try:
            threading.Thread(target=self.MQTTSEND, args=(cmd,)).start()
        except:
            if self.debug:print('failed to send via mqtt. threat start failed!')


    #Handles MQQT
    def on_message(self, mosq, obj, msg):
        if self.debug:print(msg.topic + ' ' + str(msg.payload))
        cmd = self.mqtt2plaintalk(msg.topic, msg.payload)
        if cmd:
            self.ProcessCommand(cmd)

    def mqtt_loop(self):
        waitcount = 0
        while not self.publishmqtt: #wait for mqtt connection
            time.sleep(10)
            waitcount+=1
            if waitcount==20:
                print('failed to get mqtt credentials, mqtt publishing will be disabled.')
        while True:
            if self.debug:print('starting mqtt communication')
            try:
                mqtt_client = paho.Client()
                mqtt_client.on_message = self.on_message
                mqtt_client.connect(self.mqttbroker)
                if self.debug:print ('subscribing to: ' + self.instancename + '/node/' + self.address + '/#')
                mqtt_client.subscribe(self.instancename + '/#', 2) # all topics
                #mqtt_client.publish(self.instancename + '/node/' + self.address, self.address, 0, 1) # annunciate
                mqtt_client.publish(self.instancename + '/node/' + self.address + '/routing', "node/" + self.address, 0,1)

                return_code = 0
                while return_code == 0:
                    return_code = mqtt_client.loop()
            except Exception as ex:
                if self.debug:print ('error in mqtt loop')
                if self.debug:print(ex)
                time.sleep(20)

    def messageloop(self):
        while True:
            try:
                if self.debug:print('starting gateway discovery...')
                MYPORT = 50000
                s = socket(AF_INET, SOCK_DGRAM)
                s.bind(('', MYPORT))
                while 1:
                    try:
                        data, wherefrom = s.recvfrom(1024, 0)
                        if self.debug:print('found gateway')
                        if data and self.ProcessCommand:
                            self.ProcessCommand(data)
                            return
                    except Exception as ex:
                        if self.debug:print(str(ex))
            except Exception as ex:
                if self.debug:print(str(ex))
                if self.debug:print('will retry after 20 seconds...')
                time.sleep(20)

    def waiter(self):
        if time.time()-self.last>5:
            if self.on_connected:
                self.on_connected()
        else:
            threading.Timer(3, self.waiter).start()


    def ProcessCommand(self, cmd):
        self.last = time.time()
        if cmd=='disconnected':
            if self.debug:print('Lost Connection to Gateway')
            self.CP = None
            self.client = None
            threading.Thread(target=self.messageloop).start()
            return
        words = split(cmd)
        Address = words[0]
        Command = words[1]
        Params = words[2:-1]
        Sender = words[-1]

        msg = {
            'address' : Address,
            'command': Command,
            'params': Params,
            'sender': Sender
        }
        if Command == 'cp_ip':
            if not self.CP:
                self.CP = Params[0]
                self.send('cp', 'RoutingVia', 'node/'+self.address)
                if self.debug:print('gateway ip adress:'+self.CP)
        elif Command == 'ack':
            self.send('cp', 'getirdevices')
            self.waiter()
        elif Command == 'irdevices':
            self.send('cp', 'getnodes', 'all')
        elif Command == 'nodes':
            try:
                for node in Params:
                    if len(filter(lambda n: n['node']==node, self.nodes)) == 0:
                        self.nodes.append({'node': node})
                        self.send('cp', 'getrouter', node)
                    time.sleep(1) #todo remove delay and replace with queue
            except Exception as ex:
                if self.debug:print(str(ex))
        elif Command == 'router':
            node = filter(lambda n: n['node'] == Params[0], self.nodes)[0]
            node['router'] = Params[1]
            self.send(node['node'], 'getnoports')
            self.send(node['node'], 'get', 'ports')
            print('getting router for:' + node['node'])
        elif Command == 'mqttregister':
            if len(filter(lambda n: n['node']==Params[0], self.nodes)) == 0:
                node1 = {'node': Params[0], 'router': Params[1]}
                self.nodes.append(node1)
                self.send(node1['node'], 'getnoports')
                self.send(node1['node'], 'get', 'ports')
                print('registering:' + node1['node'])
        elif Command == 'noports' and self.address=='remote':
            try:
                noports = int(Params[0])
                node = filter(lambda n: n['node'] == Sender, self.nodes)[0]
                if not 'ports' in node:
                    node['ports'] = []
                for port in range(0, noports):
                    if len(filter(lambda p: p['port']==str(port), node['ports']))==0:
                        node['ports'].append({'port': str(port)})
                if not 'completed' in node:
                    for port in range(0, noports): #todo remove delay and introduce queue
                        self.send(Sender, 'getportvalue', str(port))
                        time.sleep(0.5)
                        self.send(Sender, 'getportproperties', str(port))
                        time.sleep(0.5)
            except:
                if self.debug:print('process: error: node not found')

        elif Command == 'portproperties' and self.address=='remote':
            node = filter(lambda n: n['node'] == Sender, self.nodes)[0]
            port = filter(lambda p: p['port'] == Params[0], node['ports'])[0]
            port['type'] = Params[1]
            port['direction'] = Params[2]
            if len(node['ports'])-1==int(Params[0]):
                node['completed'] = True

        elif Command == 'portvalue' and self.address=='remote':
            node = filter(lambda n: n['node'] == Sender, self.nodes)[0]
            if len(node['ports'])-1==int(Params[0]):
                node['completed'] = True
            if not 'ports' in node:
                    node['ports'] = [{'port': Params[0]}]
            try:
                port = filter(lambda p: p['port'] == Params[0], node['ports'])[0]
                port['value'] = Params[1]
            except:
                if len(Params)==2:
                    node['ports'].append({'port': Params[0], 'value': Params[1]})

        if self.process:
            self.process(msg)