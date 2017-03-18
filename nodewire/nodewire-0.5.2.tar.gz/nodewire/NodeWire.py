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
import requests
from nodewire.splitter import split, getsender, getnode
from nodewire.tcpclient import TCPClient

debug = False # False for deployment

class Message:
    def __init__(self, msg):
        words = split(msg)
        self.Address = words[0]
        self.Command = words[1]
        self.Params = words[2:-1]
        self.Sender = words[-1]

    def __str__(self):
        return self.Address + ' ' + self.Command + ' ' + ' '.join(p for p  in self.Params) + ' ' + self.Sender


class NodeWire:
    def __init__(self, node_name='node', account=None, password=None, gateway=None, process=None):
        self.name = node_name
        self.address = self.name
        self.client = None
        self.terminated = False


        if gateway:
            self.gateway = gateway
            self.address = self.gateway + ':' + self.name

        if password and account:
            with requests.Session() as s:
                res = s.post('http://cloud.nodewire.org:5001/login', data={'email': account, 'pw': password})
                if res.url != u'http://cloud.nodewire.org:5001/login':
                    r = s.get('http://cloud.nodewire.org:5001/config').json()
                    self.gateway = str(r['instance'])
                    self.address = self.gateway + ':' + self.name

        self.process = process
        self.on_connected = None
        self.debug = False

        self.send('cp', 'ThisIs')

    def send(self, Node, Command, *Params):
        if self.client:
            try:
                cmd = Node + ' ' + Command + ' ' + ' '.join(param for param in Params) + (' ' + self.address if len(Params) != 0 else self.address)
                if self.debug:print(cmd)
                self.client.send(cmd+'\n')

            except Exception as ex:
                self.client = None
                if self.debug:print('failed to send command over LAN')
        else:
            if self.debug:print('starting TCP communication')
            self.client = TCPClient('localhost') if debug else TCPClient()
            self.client.connect()
            if self.process_command:
                self.client.received = self.process_command
                threading.Thread(target=self.client.receive, args=(1000,)).start()
            try:
                cmd = Node + ' ' + Command + ' ' + ' '.join(param for param in Params) + (' ' + self.address if len(Params) != 0 else self.address)
                if self.debug:print(cmd)
                self.client.send(cmd)
            except:
                self.CP = None
                self.client = None
                if self.debug:print('failed to send command over TCP')

    def waiter(self):
        if time.time()-self.last>5:
            if self.on_connected:
                self.on_connected()
        else:
            threading.Timer(3, self.waiter).start()

    def process_command(self, cmd):
        self.last = time.time()
        if cmd=='disconnected':
            if self.debug:print('Lost Connection to Gateway')
            self.client = None
            return

        msg = Message(cmd)

        if msg.Command == 'ack':
            self.waiter()
        elif msg.Command == 'ping':
            self.send(msg.Sender, 'ThisIs')

        if self.process:
            self.process(msg)


if __name__ == '__main__':
    nw = NodeWire('pyNode', account='sadiq.a.ahmad@gmail.com', password='secret')
    nw.debug = True
    while not nw.terminated:
        time.sleep(20)