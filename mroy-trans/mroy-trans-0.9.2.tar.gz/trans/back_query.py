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


def mm(d, *delete):
    # print(d,type(d))
    if isinstance(d, dict):
        for k in d:
            if k in delete:
                continue 
            m = ''.join(list(mm(d[k], *delete)))
            # print(m, type(m))
            if isinstance(d[k], list) and len(d[k]) == 1:
                yield k + ": " + m + "\n"
            elif isinstance(d[k], (dict,list)):
                yield  m + "\n"
            else:
                yield k + ": " + m + "\n"
            
    elif isinstance(d, list):
        for i in d:
            m = ''.join(mm(i,*delete))
            # print(m,type(m))
            yield m 
    elif isinstance(d, str):
        # print(d,'s')
            yield d + ","
    

def trans(msg,win=False):
    global data_tem
    data_tem['query'] = msg
    res = to(host, method='post',data=data_tem)
    msg = res.json()
    # L.i(msg)
    f = msg['trans_result']['from']
    if f == 'zh':
        imsg = '[{fr}->en]:{res}'.format(
            fr=f,
            # to=msg['trans_result']['to'],
            res=res.json()['trans_result']['data'][0]['dst'] +'\n',
            # phonec=ph,
        )
        return imsg.split(":")

    data_tem['from'] = f
    res = to(host, method='post',data=data_tem).json()
    data_tem['from'] = 'auto'
    # print(res,res['dict_result'])
    try:
        dat = ''.join(mm(res['dict_result']['simple_means']['symbols'], 'ph_en_mp3','ph_am_mp3','ph_tts_mp3'))
    except (TypeError, KeyError) as e:
        dat = ''
    # print('sds',res)
    for data in res['trans_result']['data']:
        L.i(data['dst'])
        if win:
            imsg = '{res}'.format(
                res=data['dst'] + '\n'+dat,
            )
        else:
            imsg = '{res}'.format(
                res=data['dst'] ,
            )
        t = '[{fr}->{to}]'.format(
            fr=f,
            to=msg['trans_result']['to'],
            )
    print(imsg)
    return t, imsg



# msg = ' '.join(sys.argv[1:])
class Clip(threading.Thread):
    def __init__(self, root,text):
        self.root_ui = root
        self.text = text
        # print(self.root_ui['width'],self.root_ui['height'])
        super(Clip, self).__init__()

    def run(self):
        # sleep()
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
            t,msg = trans(msg,True)    
            self.text.insert(0.0, t + ":"+msg+"\n")
            self.text.pack()

def urun():
    try:
        from Tkinter import Tk,Text,Frame
    except ImportError:
        from tkinter import Tk,Text,Frame
    root = Tk()
    # root['width'] = 100
    # root['height'] = 200
    root.geometry('200x400')
    windowFrame=Frame(root,width=100,height=200)
    windowFrame.pack()
    text = Text(windowFrame,width=100)
    text.pack()
    c = Clip(root, text)
    c.start()
    root.mainloop()
    


def brun():
    m = """
osascript -e 'display notification \"{msg}\" with title \"Tr\"  subtitle \"{s}\" sound name \"Blow\" '

    """
    # 
    while True:
        sleep(1)
        msg = read_msg()
        if not msg:
            continue
        # data_tem['query'] = msg
        # res = to(host, method='post',data=data_tem)
        # for data in res.json()['trans_result']['data']:
            # L.i("\n",data['dst'])
        t,res = trans(msg)
        res = res.replace('"','').replace("\n",' ')
        print( m.format(msg=res,s=t))
        if len(res) > 20:
            c = int(len(res) /20)
            for i in range(0,c):
                b = res[i* 20: (i+1) *20]
                os.popen( m.format(msg=b,s=t))
        else:
            os.popen( m.format(msg=res,s=t))
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