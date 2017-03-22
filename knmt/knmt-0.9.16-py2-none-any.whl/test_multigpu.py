import chainer
import cupy
import time
from cupy.cuda import Device

import threading
import Queue
import multiprocessing

import argparse
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("size", type = int)
parser.add_argument("gpu", nargs = "+", type = int)
args = parser.parse_args()

print "runnig exp with matrix size %i , on gpus %r"%(args.size, args.gpu)
t0 = time.clock()

x_list = {}
for n in args.gpu:
    print "creating data", n
    t1 = time.clock()
    with Device(n):
        t2 = time.clock()
        x = cupy.ones((args.size, args.size), dtype = cupy.float32)
        x_list[n] = x
    t3 = time.clock()
    print "time one creation:", t2-t1, t3-t2
 
for n in args.gpu:
    with Device(n):
        cupy.cuda.runtime.streamSynchronize(0)
t_sync1 = time.clock()
print "sync 1", t_sync1 - t0
 
 
def run_comp(n, appender):
    print "processing gpu", n
    t1b = time.clock()
    with Device(n):
        t2b = time.clock()
        print "using gpu", n
        x = x_list[n]
        t = x.dot(x)
        t += x.dot(x)
        print "middle_comp gpu", n
        t += x.dot(x)
        t += x.dot(x)
        t += x.dot(x)
        print "appending gpu", n
        appender(t)
    t3b = time.clock()
    print "time one comp:", t3b-t1b
    
# 
# 
# for u in theurls:
#     t = threading.Thread(target=get_url, args = (q,u))
#     t.daemon = True
#     t.start()


if 1:
    thread_class = threading.Thread
    queue_class = Queue.Queue
else:
    thread_class = multiprocessing.Process  
    queue_class = multiprocessing.Queue
    
q = queue_class()
res_list = []           
for n in args.gpu:
    t = thread_class(target = run_comp, args = (n, q.put))
#     t.daemon = True
    t.start()
res_list = []
while len(res_list) < len(args.gpu):
    res_list.append(q.get(block = True))

print "res_list filled"
    
# res_list = []           
# for n in args.gpu:
#     run_comp(n, appender = res_list.append)
    
for n in args.gpu:
    with Device(n):
        cupy.cuda.runtime.streamSynchronize(0)
        
t_sync2 = time.clock()
print "sync 2", t_sync2 - t_sync1
    
t4 = time.clock()   
print "computed all", len(res_list), t4-t0
print "summing across gpus:"
for i, n in enumerate(args.gpu[1:]):
    print "adding", i+1, n
    with Device(chainer.cuda.get_device(res_list[0])):
        t = res_list[i+1].copy()
        res_list[0] += t
t5a = time.clock()
print res_list[0]
t5 = time.clock()
print "sync time", t5-t5a
print "total_sum", t5-t4
print "total", t5-t0
    