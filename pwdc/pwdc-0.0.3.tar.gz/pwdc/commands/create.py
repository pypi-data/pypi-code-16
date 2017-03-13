"""Play With Docker Client - Create Command."""


from json import dumps
from .base import Base



import os
import sys

import requests

import yaml
from datetime import date, time, datetime, timedelta

from pprint import pprint
import logging
import re
from subprocess import Popen, PIPE
import click

from .. import utils


class Create(Base):
   

    def create_session(self):
        global session
        self.utils.blue("- create_session")
        resp = requests.post( self.utils.pwd_url )
        if resp.status_code != 200:
            print "Create Session error"
            raise BaseException('POST ' + self.utils.pwd_url + " = " + format(resp.status_code))
        else:
            try:
                id = re.search('.*/p/(.+)$', resp.url).group(1)
            except AttributeError:
                raise BaseException('session not found in ' + resp.url)
            print "Create Session ok " + self.utils._url('/p/'+id)
            self.utils.session['id'] = id
            pprint (self.utils.session)
        return self.utils.ok

    def create_instance(self, i):
        global session
        self.utils.blue("- create_instance " + str(i))
        resp = requests.post( self.utils._url("/sessions/{:s}/instances".format(self.utils.session['id'])) )

        if resp.status_code == 500:
            self.utils.rm_session()
            BaseException("Erreur 500, surement la session existe plus")
        elif resp.status_code == 409:
            print "Max number instances is reached"
            return self.utils.ko
        elif resp.status_code != 200:
            # This means something went wrong.
            resp.raise_for_status()
            raise BaseException('GET '+ self.utils.pwd_url + "/sessions/" + self.utils.session['id'] + "/instances = " \
                            + format(resp.status_code) + format(resp.headers))
        else:
            print('Created session ok with. IP: {}'.format(resp.json()["ip"]))        
            self.utils.session['ip'+str(i)] = resp.json()["ip"]
            res = self.utils.write_session()
            assert res == self.utils.ok
        return self.utils.ok


    def init_swarm(self):
        global session
        self.utils.blue ("- init_swarm")
        if not 'ip1' in self.utils.session:
            print "Session is not correctly initialised"
            return self.utils.ko

        os.environ['DOCKER_HOST'] = 'tcp://pwd' + self.utils.session["ip1"].replace(".", "_")  + '-2375.' + self.utils.pwd_dns + ':80'

        if self.options["-d"] == True:
            print "DOCKER_HOST="+os.environ['DOCKER_HOST']    
        try:
            out=""
            p = Popen('docker swarm init --advertise-addr %s' % (self.utils.session["ip1"]), shell=True, stdout=PIPE, stderr=PIPE)
            if p.wait() != 0:
                raise RuntimeError(p.stderr.read())            
            for line in p.stdout:
                if self.options["-d"] == True:
                    print ": "+line,
                if line.find("    ") != -1:
                    out += line
            if self.options["-d"] == True:
                print "out = '"+out.strip(' \t\r\n')+"'"
            self.utils.session['join'] = out.strip(' \t\r\n')
            self.utils.write_session()
        except RuntimeError as e:
            self.utils.red(str(e))

    def join_swarm(self, i):
        self.utils.blue ("- join_swarm - node" + str(i))

        if not 'ip'+str(i) in self.utils.session:
            print "Session is not correctly initialised"
            return self.utils.ko

        if not 'join' in self.utils.session:
            print "You must run init_swarm before adding a node"
            return self.utils.ko

        #Connect on node i
        os.environ['DOCKER_HOST'] = 'tcp://pwd' + self.utils.session["ip"+str(i)].replace(".", "_")  + '-2375.' + self.utils.pwd_dns + ':80'
        print "DOCKER_HOST="+os.environ['DOCKER_HOST']
        try:
            p = Popen(self.utils.session["join"], shell=True, stdout=PIPE, stderr=PIPE)
            if p.wait() != 0:
                raise RuntimeError(p.stderr.read())
                for line in p.stdout:
                    print "p: "+line,
        except RuntimeError as e:
            self.utils.red(str(e))

        
    def run(self):

        if self.options["-d"] == True:
            print('You supplied the following options:', dumps(self.options, indent=2, sort_keys=True))

        self.utils.ping()
    
        if not self.utils.read_session():
            if self.create_session():
                res = self.utils.write_session()
                assert res == self.utils.ok

        self.utils.debug("green", "session is " + self.utils.session['id'])
        if self.utils.options["-d"] == True:
            pprint (self.utils.session)

        if self.utils.check_session() == self.utils.ko:
            self.utils.red("Your session has been deleted, please retry now")
            return self.utils.ko

        for i in range(1,6):
            if not 'ip'+str(i) in self.utils.session:
                self.utils.blue("session 'ip"+str(i)+"' does not exists ==> create it")
                if not self.create_instance(i):
                    break                
            else:
                self.utils.debug("red", "session 'ip"+str(i)+"' already exists ==> do nothing")


        self.init_swarm()
        for i in range(2,6):
            self.join_swarm(i)

        self.utils.print_welcome()
                    

