import os
import sys
import time
from contextlib import contextmanager
from termcolor import cprint,colored
from fabric.api import output, parallel
from fabric.api import task, roles, run, env, local, cd, execute, put, sudo, settings
from fabric.colors import *
from qlib.io.console import input_default,dict_cmd

PATH = os.path.dirname(__file__)
BASE_URL = os.path.join(os.getenv("HOME"), ".ssh_hosts")

from qlib.data.sql import SqlEngine
from qlib.log import LogControl as L

# env.roledefs['targets'] = ['localhost'] 

DOC = """
    Usage: Ex [host fuzz name] ,, cmd
    Example: 
        >> Ex example.host.com ,,  ls . 
        >> Ex ls .
"""



output.running = False
sql = SqlEngine(BASE_URL)
if not sql.table_list():
    sql.create("host",login="login",port="port",passwd="passwd")

def get_records(fuzz=None):
    if fuzz:
        for r in sql.search("host","login","port","passwd", login=fuzz):
            yield r
    else:
        for r in sql.select("host","login","port","passwd"):
            yield r

def par(l):
    if l:
        for i in l.split(","):
            try:
                if "-" in i:
                    yield range(int(i.split("-")[0]), int(i.split("-")[1]))
                else:
                    yield int(i)
            except TypeError:
                continue

def choose_hosts(fuzz=None):
    # print(fuzz)
    res = list(get_records(fuzz.strip()))
    # print(res)
    roles = []
    passwd = {}
    if res:
        for I,i in enumerate(res):
            L.i(i[0],tag=I)
        
        for i in  par(input_default(colored("exm: 1,2-4 >>","cyan"),'0')):
            if isinstance(i, tuple):
                for m in i:
                    roles.append(res[m][0] + ":" + res[m][1])
                    passwd[res[m][0] + ":" + res[m][1]] = res[m][2]
            else:
                roles.append(res[i][0] + ":" + res[i][1])
                passwd[res[i][0] + ":" + res[i][1]] = res[i][2]
    else:
        r = dict_cmd({
            "user":None,
            "host":None,
            "port":None,
            "passwd":None,
        })

        
        roles = [r['user'] + "@" + r['host'] + ":" + r['port']]
        if not roles:
            L.i("nil.")
            return None
        sql.insert("host",['login','port','passwd'], r['user']+"@" + r['host'],r['port'], r['passwd'])
        passwd[roles[0]] =  r['passwd']
    print(roles)
    res =  {"t": roles}
    env.roledefs.update(res)

    env.hosts = res['t']
    
    env.passwords = passwd
    



@task
@parallel
def shell(cmd, h):
    output = run(cmd,quiet=True)
    L.i('\n'+output,tag=h)

def main():
    cmd_str = ' '.join(sys.argv[1:])
    if '--help' in sys.argv:
        L.i(DOC,tag="help")
        sys.exit(0)
    if ',,' in cmd_str:
        fuzz, cmd = cmd_str.split(",,")
    else:
        cmd = cmd_str
        fuzz = input_default(colored('Host run:',"blue"),"")
    
    choose_hosts(fuzz)

    try:
        for h in  env.hosts:
            env.host_string = h
            shell(cmd,h)
    except (KeyboardInterrupt, InterruptedError) as e:
        L.ok("Bye~")
