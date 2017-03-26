import sys, os, json
from cmd import Cmd
from termcolor import colored
from Gill.utils import L


if sys.platform[:3] == "win":
    default_config_path = [os.path.join(os.getenv("HOMEPATH"),"fatezero")]
else:
    default_config_path = (
        "/usr/local/etc/fatezero",
    )

for d in default_config_path:
    if not os.path.exists(d):
        os.mkdir(d)


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

    if file == True:
        for p in default_config_path:
            if os.path.exists(p):
               with open(os.path.join(p,"config.json"), "w") as fp: fp.write(json.dumps(config))
               return config
    else:
        return config



class CLI(Cmd):

    def __init__(self, run_server=None, run_local=None):
        super(CLI, self).__init__()
        self.prompt = colored("> ","red")    # define command prompt
        self.config = get_config(default_config_path)
        self.run_server_mapper = {
            "server":run_server,
            "local":run_local,
        }

    def do_show(self, arg):
        if not arg:
            print(colored(arg,"red") + "not in config, type follow:" + colored("\n".join(self.config.keys()),"yellow" ))
        elif arg not in self.config:
            print(colored(arg,"red") + "not in config, type follow:" + colored("\n".join(self.config.keys()),"yellow" ))
        else:
            L(arg, self.config[arg],c="green", a=['bold'])

    def do_set(self, arg):
        if not arg:
            self.help_set()
            print(colored(arg,"red") + "not in config, type follow:" + colored("\n".join(self.config.keys()),"yellow" ))
        elif arg not in self.config:
            print(colored(arg,"red") + "not in config, type follow:" + colored("\n".join(self.config.keys()),"yellow" ))
        else:
            self.config[arg] = input(colored(arg,"red", attrs=['underline'])+ ": _______________" + "\b" * 17)
            build_config(**self.config)

    def complete_set(self, text, line, begidx, endidx):
        if not text:
            completions = self.config.keys()
        else:
            completions = [ i for i in self.config.keys() if i.find(text) > 0]

        #print completions
        if len(completions) == 1:
            print(completions[0])
        else:
            print("\n",colored("\t".join(completions), "green"))
        return completions

    def help_set(self):
        # print ("syntax: dir path -- displaya list of files and directories")
        print("set config's key => value. type arg : "+ colored("'set  server'", "green"))
 
    def do_quit(self, arg):
        return True 

    def help_quit(self):
        print ("syntax: quit -- terminatesthe application")

    def do_run(self, server_or_local):
        config = self.config.copy()
        config['auth'] = config.get('auth', "hello")
        config['hash'] = config.get('hash', "md5")
        if server_or_local in ["server", "local"]:
            self.run_server_mapper[server_or_local](config)
        else:
            print(colored("server", "blue"),"/",colored("local","yellow"))

    do_q  = do_quit
    do_se = do_set
    do_s = do_show
    do_r = do_run
