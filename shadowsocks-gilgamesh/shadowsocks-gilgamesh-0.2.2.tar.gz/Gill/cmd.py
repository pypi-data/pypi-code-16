import os, sys, argparse, pwd, grp
import logging
import signal
import time
import json
import argparse
from Gill import loop 
from Gill.relay import NetNode
from Gill import daemon
from Gill.protocols.dns import DNSearcher
from Gill.utils import L
from termcolor import colored

if sys.platform[:3] == "win":
    default_config_path = [os.path.join(os.getenv("HOMEPATH"),"fatezero")]
else:
    default_config_path = (
        "/usr/local/etc/fatezero",
    )

for d in default_config_path:
    if not os.path.exists(d):
        os.mkdir(d)

def set_user(username):
    if username is None:
        return

    import pwd
    import grp

    try:
        pwrec = pwd.getpwnam(username)
    except KeyError:
        logging.error('user not found: %s' % username)
        raise
    user = pwrec[0]
    uid = pwrec[2]
    gid = pwrec[3]

    cur_uid = os.getuid()
    if uid == cur_uid:
        return
    if cur_uid != 0:
        logging.error('can not set user as nonroot user')
        # will raise later

    # inspired by supervisor
    if hasattr(os, 'setgroups'):
        groups = [grprec[2] for grprec in grp.getgrall() if user in grprec[3]]
        groups.insert(0, gid)
        os.setgroups(groups)
    os.setgid(gid)
    os.setuid(uid)


# def run_local(config):
#     n = NetNode(test_config, is_local=True)
#     l = Loop()
#     n.add_to_loop(l)
#     l.run()



def run_local(config):
    daemon.daemon_exec(config)
    if "local_address" not in config:
        config['local_address'] = '127.0.0.1'
    try:
        logging.info("starting local at %s:%d" %
                     (config['local_address'], config['local_port']))

        
        tcp_server = NetNode(config, is_local=True)
        
        eloop = loop.Loop()
        tcp_server.add_to_loop(eloop)
        # udp_server.add_to_loop(loop)

        def handler(signum, _):
            logging.warn('received SIGQUIT, doing graceful shutting down..')
            tcp_server.close(next_tick=True)
            udp_server.close(next_tick=True)
        signal.signal(getattr(signal, 'SIGQUIT', signal.SIGTERM), handler)

        def int_handler(signum, _):
            sys.exit(1)
        signal.signal(signal.SIGINT, int_handler)

        daemon.set_user(config.get('user', None))
        eloop.run()
    except Exception as e:
        print(e)
        sys.exit(1)


def run_server(config, is_local=False):
    daemon.daemon_exec(config)
    if 'port_password' in config:
        if 'password' in config:
            logging.warn('warning: port_password should not be used with '
                         'server_port and password. server_port and password '
                         'will be ignored')
    else:
        config['port_password'] = {}
        server_port = config['server_port']
        if type(server_port) == list:
            for a_server_port in server_port:
                config['port_password'][a_server_port] = config['password']
        else:
            config['port_password'][str(server_port)] = config['password']

    tcp_servers, udp_servers=[], []
    port_password = config['port_password']
    for port, password in port_password.items():
        a_config = config.copy()
        a_config['server_port'] = int(port)
        a_config['password'] = password
        logging.info("starting server at %s:%d" %
                     (a_config['server'], int(port)))
        tcp_servers.append(NetNode(a_config, is_local=is_local))
        # udp_servers.append(udprelay.UDPRelay(a_config, dns_resolver, False))


    def child_handler(signum, _):
        logging.warn('received SIGQUIT, doing graceful shutting down..')
        list(map(lambda s: s.close(next_tick=True),
                 tcp_servers + udp_servers))
    signal.signal(getattr(signal, 'SIGQUIT', signal.SIGTERM),
                  child_handler)

    def int_handler(signum, _):
        sys.exit(1)
    signal.signal(signal.SIGINT, int_handler)

    try:
        eloop = loop.Loop()
        list(map(lambda s: s.add_to_loop(eloop), tcp_servers + udp_servers))

        set_user(config.get('user', None))
        eloop.run()
    except Exception as e:
        print(e)
        sys.exit(1)

def get_config(possible_dir):
    for pd in possible_dir:
        for r,d,fs in os.walk(pd):
            for f in fs:
                if f == "config.json":
                    with open(os.path.join(r,f)) as fp:
                        return json.loads(fp.read())
    
    return None


def build_config(file=False, **kargs):
    config = {
        "server":None,
        "server_port":None,
        "local_port":None,
        "password":None,
        "method":None,
        "timeout":None,
        
    }


    def d_input(pre,default=''):
        r = input(pre + ": {}".format(colored(default,'red')))
        if r:
            return r.strip()
        return default

    config.update(kargs)
    tmp = dict()
    for k in config:
        if not config[k]:
            if k == "server":
                v = d_input(k,"0.0.0.0")
            elif k == "server_port":
                v = int(d_input(k,19748))
            elif k == "local_port":
                v = int(d_input(k,10800))
            elif k == "timeout":
                v = int(d_input(k,600))
            elif k == "password":
                v = d_input(k)
                while  not v:
                    v = d_input(k)
            else:
                v = d_input(k)

            tmp.update({k:v})

    config.update(tmp)
    
    file = d_input("if save to local:",True)

    if file:
        for p in default_config_path:
            if os.path.exists(p):
               with open(os.path.join(p,"config.json"), "w") as fp: fp.write(json.dumps(config))
               return config
    else:
        return config


def get_args():
    DOC = """
      thia is a proxy tool named Gilgamersh.
        the oldest king of human.
        there are some precise tool as protocols.
        ea (Enuma Elish)
        chains of heaven 

    """
    parser = argparse.ArgumentParser(usage="how to use this", description=DOC)
    parser.add_argument("-c", "--config-path", default=default_config_path, help="specify config path")
    parser.add_argument("-B", "--build", default=False, action="store_true", help="daemon mode")
    parser.add_argument("-p", "--password", default=None, help="set password")
    parser.add_argument("-t", "--timeout", default=600, help="set timeout, deault is 600.")
    parser.add_argument("-m", "--method", default="aes-256-cfb", help="set method, deafult aes-256-cfb")
    parser.add_argument("-ha", "--hash", default='md5', help="set hash method, deafult md5")
    parser.add_argument("-a", "--auth", default="hello", help="set auth, deafult hello")
    parser.add_argument("-s", "--server", default="0.0.0.0", help="set server port, default is 19748")
    parser.add_argument("-sp", "--server-port", default=19748, help="set server port, default is 19748")
    parser.add_argument("-lp", "--local-port", default=10800, help="set local port, default 10800")
    parser.add_argument("-S", "--server-mode",default=False, action="store_true", help="start server")
    parser.add_argument("-L", "--local-mode",default=False, action="store_true", help="start server")
    parser.add_argument("-D", "--daemon",default=False, action="store_true", help="start server daemon")
    parser.add_argument("--stop", default=False, action="store_true", help="stop server daemon")
    # parser.add_argument("-e", "--event", default=False, action="store_true", help="event mode")
    return parser.parse_args()


def main():
    Args = get_args()
    config = None
    if Args.build:
        L("building..",c="green")
        config  = build_config(
            server=Args.server,
            server_port=Args.server_port,
            method=Args.method,
            local_port=Args.local_port,
            auth=Args.auth,
            timeout=Args.timeout,
            password=Args.password)
        sys.exit(0)
        
    if Args.config_path:
        L("search config..",c="green")
        config = get_config(Args.config_path)
    else:
        L("search config..",c="green")
        config = get_config(default_config_path)
    if not config :
        L("not found config.json :",default_config_path, c="red")
        L("build config")
        config  = build_config(
            server=Args.server,
            server_port=Args.server_port,
            method=Args.method,
            local_port=Args.local_port,
            auth=Args.auth,
            timeout=Args.timeout,
            password=Args.password)
    if Args.daemon:
        config["daemon"] = 'start'
    elif Args.stop:
        config["daemon"] = 'stop'

    config['workers'] = config.get('workers', 1)
    config['pid-file'] = config.get('pid-file', '/usr/local/var/run/shadowsocks.pid')
    config['log-file'] = config.get('log-file', '/usr/local/var/log/shadowsocks.log')
    config['auth'] = config.get('auth', Args.auth)
    config['hash'] = config.get('hash', Args.hash)

    if Args.server_mode:
        config["server"] = DNSearcher()[config["server"]]
        L("config:", config,c="blue")
        run_server(config)
    elif Args.local_mode:
        config["server"] = DNSearcher()[config["server"]]
        L("config:", config,c="blue")
        run_local(config)

