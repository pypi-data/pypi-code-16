import sys,argparse,os
from time import sleep 
from qlib.net import to
from qlib.log import LogControl as L
from qlib.asyn.daemon import run,restart, stop

import time,threading

host = 'fanyi.baidu.com/v2transapi'
data_tem = {
    'from': 'auto',
    'to': 'zh',
    'query': None,
    'transtype':'translang', 
    'simple_means_flag':'3',
}
old = ''
path = os.path.dirname(__file__)
def read_msg():
    global old
    msg = os.popen("pbpaste").read()
    if msg != old:
        old = msg
        return msg


# msg = ' '.join(sys.argv[1:])
class Clip(threading.Thread):
    def __init__(self, root,text):
        self.root_ui = root
        self.text = text
        super(Clip, self).__init__()

    def run(self):
        sleep(2)
        self.root_ui
        old = ''
        while 1:
            sleep(1)
            try:
                msg = self.root_ui.clipboard_get()
                if msg == old:
                    continue
                else:
                    old = msg
            except RuntimeError:
                break
            data_tem['query'] = msg
            res = to(host, method='post',data=data_tem)
            for data in res.json()['trans_result']['data']:
                L.i(data['dst'])
                self.text.insert(0.0, data['dst']+"\n")
                self.text.pack()

def urun():
    try:
        from Tkinter import Tk,Text
    except ImportError:
        from tkinter import Tk,Text
    root = Tk()
    text = Text(root)
    text.pack()
    c = Clip(root, text)
    c.start()
    root.mainloop()
    


def brun():
    while True:
        sleep(1)
        msg = read_msg()
        if not msg:
            continue
        data_tem['query'] = msg
        res = to(host, method='post',data=data_tem)
        for data in res.json()['trans_result']['data']:
            L.i("\n",data['dst'])
            
            os.popen( path + "/msg "+ data['dst'])
            # to("http://localhost:8080/",data=data,method='post')

def srun():
    while True:
        sleep(1)
        msg = read_msg()
        if not msg:
            continue
        data_tem['query'] = msg
        res = to(host, method='post',data=data_tem)
        for data in res.json()['trans_result']['data']:
            L.i("\n",data['dst'])
            
            # os.popen( path + "/msg "+ data['dst'])
            to("http://localhost:8080/",data=data,method='post')



if __name__ == '__main__':
    args = get_args()
    if args.start:
        run(brun)
    elif args.stop:
        stop(brun)
    elif args.restart:
        restart(brun)
    else:
        brun()