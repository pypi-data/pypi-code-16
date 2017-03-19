#!/usr/bin/env python
'''
Copyright (c) 2016-2017, nodewire.org
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
import serial
import glob
import sys
import threading
import time
if sys.version[0] == '2':
    from Queue import Queue as queue
else:
    from queue import Queue as queue
import configparser
import requests
from nodewire.splitter import split, getnode, getsender, getinstance, getfulladdress, getsenderonly, getnodeonly, getfullsender
from nodewire.tcpclient import TCPClient

debug = False

config = configparser.RawConfigParser()
try:
    config.read('cp.cfg')
except:
    print('could not find cp.cfg')
    print('please run from a directory that contains this file')
    quit()

instancename = None
mqttbroker = None

user = str(config.get('user', 'account_name'))
password = str(config.get('user', 'password'))

client = TCPClient('localhost') if debug else TCPClient()

def openSerial():
    tries = 10
    print('searching for serial port...')

    while True:
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')
        sys.stdout.write(".")
        sys.stdout.flush()
        # ports = serial_ports()
        for port in ports:
            try:
                serialport = serial.Serial(port, 38400, timeout=1)
                serialport.reset_input_buffer()
                serialport.write('any ping cp\n'.encode())
                time.sleep(2)
                msg = serialport.readline().decode()
                if msg.startswith('cp ThisIs')  or msg.startswith('remote ThisIs') :
                    print(bcolors.BOLD + 'serialport is on ' + port + bcolors.ENDC)
                    return serialport
                serialport.close()
            except Exception as exc:
                pass
        tries-=1
        if tries == 0:
            print(bcolors.FAIL + 'giving up on serial port. will not support serial devices in this run' + bcolors.ENDC)
            return None
        time.sleep(30)

ser = None #serial.Serial('/dev/ttyACM1', timeout =5)

def _readline():
    eol = b'\n'
    leneol = len(eol)
    line = bytearray()
    while True:
        c = ser.read(1)
        if c:
            ser.write(c) #todo check collision avoidance
            line += c
            if line[-leneol:] == eol:
                ser.write(eol)
                break
    return bytes(line)

#uart loop
#handles the zigbee network.
def uart_loop():
    global buff, ser
    print('running uart thread')
    while True:
        ser = openSerial()
        while True:
            try:
                if ser:
                    cmd = _readline().decode().strip() # ser.readline()
                    print(bcolors.HEADER + cmd + bcolors.ENDC)
                    if cmd.strip() != "":
                        sender = getsender(cmd)
                        sendero =  getsenderonly(cmd)
                        cmd = cmd.replace(sender, sendero)
                        client.send(cmd)
            except Exception as Ex:
                print(bcolors.FAIL + 'error reading uart:' + str(Ex) + bcolors.ENDC)
                ser = None
                break

sendqueue = queue()
def uart_send():
    while True:
        response = sendqueue.get()
        if ser:
            ser.write((response+'\n').encode())
            print(bcolors.OKBLUE + response + bcolors.ENDC)
        time.sleep(0.2)
        sendqueue.task_done()

def tcp_received(data):
    if data == 'disconnected':
        print(bcolors.WARNING + 'Lost Connection to Gateway' + bcolors.ENDC)
        time.sleep(10)
        tcp()
    else:
        datas = data.splitlines()
        for data in datas:
            node = getnode(data)
            if ':' in node:
                nodeonly = node.split(':')[1]
                data = data.replace(node, nodeonly).strip()
            sendqueue.put(data)

def tcp():
    print('starting TCP connection')
    client.connect()
    client.received = tcp_received
    client.send('cp Gateway ' + instancename)
    threading.Thread(target=client.receive, args=(1000,)).start()

class ucolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class wcolors:
    HEADER = ''
    OKBLUE = ''
    OKGREEN = ''
    WARNING = ''
    FAIL = ''
    ENDC = ''
    BOLD = ''
    UNDERLINE = ''

if sys.platform.startswith('win'):
    bcolors = wcolors
else:
    bcolors = ucolors

if __name__ == '__main__':
    print(bcolors.BOLD + 'NodeWire Gateway' + bcolors.ENDC)
    print('version 0.5 alpha')
    print('Copyright 2017 nodewire.org')
    print('starting...')

    while True:
        with requests.Session() as s:
            try:
                server = 'http://45.55.150.77:5001'
                res = s.post(server + '/login', data={'email': user, 'pw': password})
                if res.ok:
                    r = s.get(server + '/config').json()
                    instancename = str(r['instance'])
                    break
                else:
                    print(bcolors.FAIL + 'authentication failure' + bcolors.ENDC)
                    quit()
            except:
                print(bcolors.WARNING + 'could not connect to cloud service. will retry after 30 seconds.' + bcolors.ENDC)
                time.sleep(30)
    tcp()
    threading.Thread(target=uart_send).start()
    uart_loop()
