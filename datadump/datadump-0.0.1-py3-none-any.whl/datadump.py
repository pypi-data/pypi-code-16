import pickle
import os

print('''Workspace is tmp/ folder by default. Use 

datadump.swd("/path/to/workspace/") 

to change this. ''')

__WORK_DIR__ = "tmp/"

def wd(): 
    global __WORK_DIR__
    return __WORK_DIR__

def pwd(): 
    global __WORK_DIR__
    print(__WORK_DIR__)

def swd(s):
    global __WORK_DIR__
    if s[-1] == '/': 
        __WORK_DIR__ = s
    else: 
        __WORK_DIR__ = s + '/'

def save(name, *args, **kwargs): 
    global __WORK_DIR__
    os.makedirs(__WORK_DIR__, exist_ok=True)
    t = (args, kwargs)
    with open('{}{}.pkl'.format(__WORK_DIR__, name), 'wb') as f: 
        pickle.dump(t, f)
    return t

def load(name): 
    global __WORK_DIR__
    with open('{}{}.pkl'.format(__WORK_DIR__, name), 'rb') as f: 
        t = pickle.load(f)
    return t

