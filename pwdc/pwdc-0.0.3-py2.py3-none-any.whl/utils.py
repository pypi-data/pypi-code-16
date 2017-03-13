
import sys
import os
from os.path import expanduser
import json
from pprint import pprint
import requests



class Utils(object):
    
    R="\033[31m"
    G="\033[32m"
    B="\033[36m"
    N="\033[m"

    ok=1
    ko=0

    config_file=expanduser("~")+"/.pwdc"
    config = {}

    #Default param will be overide by ~/.pwdc
    pwd_url="http://mustbeconfigured.com"

    session_file="./.session"
    session = {}

    def __init__(self, options):
        self.options = options
        self.session_file = options["--session_file"]

        self.check_config_file()

        self.debug("blue", "pwd_url is " + self.pwd_url)
        self.pwd_dns = self.pwd_url[self.pwd_url.find("://")+3:]


    def check_config_file(self):
        #Do we need to update config_file ?
        if self.options["--pwd-url"]:
             self.config["pwd_url"] = self.options["--pwd-url"]
             self.write_config_file()

        #Read Config file
        if not os.path.isfile(self.config_file):
            #init default
            self.red("You need configure pwdc with 'pwdc init --pwd-url=http://xxx' or configure '~/.pwdc'")
            #raise RuntimeError("configuration file ko ~/.pwdc")
            sys.exit(-1)
            #self.config["pwd_url"] = self.pwd_url
            #self.write_config_file()

        #Read file and init
        self.read_config_file()


    def read_config_file(self):
        with open(self.config_file) as f:
            self.config = json.load(f)
            if "pwd_url" in self.config:
                self.pwd_url = self.config["pwd_url"]
            else:
                if self.options["-d"] == True:
                    pprint(self.config)
                raise BaseException('no pwd_url in config ??? ') 


    def write_config_file(self):
        self.debug("blue", "Write_config_file" + self.options["--pwd-url"])
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)
        if self.options["-d"] == True:
            pprint(self.config)

## Print Messages

    def blue(self,msg):
        print self.B+msg+self.N
    def red(self,msg):
        print self.R+msg+self.N
    def green(self,msg):
        print self.G+msg+self.N

    print_color = {
        "blue"  : blue,
        "red"   : red, 
        "green" : green
    }
    def debug(self,c, msg):
        if self.options["-d"] == True :
            self.print_color[c](self, msg)



    def print_welcome(self):
        self.blue("1. You can View your session in a Browser")
        self.green(self.pwd_url+'/p/'+self.session['id'])
    
        if 'ip1' in self.session:
            print ""
            self.blue ("2. You can interract with your cluster bu executing :")
            self.green ('eval $(pwdc env)')
            self.blue ("Then just uses your classic docker client!!")


##Session Management


    def _url(self, path):
        return self.pwd_url + path

    def ping(self):
        self.blue("You are working with PWD : " + self.pwd_url)
        resp = requests.get( self._url("/ping") )
        assert resp.status_code == 200
#        self.debug("blue" ,"PWD server is UP :)")
        self.green(" --> PWD server is UP :)")


    def check_session(self):
        self.debug("blue", "- check_session")
        resp = requests.get( self._url("/sessions/" + self.session['id']) )
        if resp.status_code != 200:
            self.red ("Problem With session, you need to create NewOne")
            self.rm_session()
            return self.ko
        return self.ok



##Session File Management


    def read_session(self):
        self.debug("blue", "- read_session in file " + self.session_file)

        #path="."
        #for file in os.listdir(path):
            #if file.lower() == ".session" and os.path.isfile(os.path.join(path, file)):
            #with open(os.path.join(path, file)) as f:
        if os.path.isfile(self.session_file):
            with open(self.session_file) as f:
                self.session = json.load(f)
                if self.options["-d"] == True:
                    pprint(self.session)
                return self.ok
        return self.ko

    def write_session(self):
        self.debug("blue", "- write_session in file " + self.session_file)
        if self.options["-d"] == True:
            pprint(self.session)
        with open(self.session_file, 'w') as f:
            json.dump(self.session, f)
            return self.ok
        return self.ko

    def rm_session(self):
        self.blue("- rm_session file " + self.session_file)
        if os.path.isfile(self.session_file):
            os.remove(self.session_file)
        self.session= {}


    def pwd_init(self):

        self.ping()
    
        if not self.read_session():
            self.red("No PWD Session, check --session_file parameter")
            return self.ko

        if self.check_session() == self.ko:
            self.red("Your session has been deleted, please retry now")
            return self.ko

        self.green("session is " + self.session['id'])
        if self.options["-d"] == True:
            pprint (self.session)
        return self.ok
