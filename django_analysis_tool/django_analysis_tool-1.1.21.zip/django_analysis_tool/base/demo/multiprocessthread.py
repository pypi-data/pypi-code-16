#! usr/bin/env python
# coding=utf-8

from multiprocessing import Pool
import multiprocessing
from time import sleep
import time
import threadpool,platform

def runer(atom):
    for i in range(10):
        print ("{}-----{}\n".format(i, atom))
        sleep(1)

def threadworker(L):
    if "64" in ",".join(platform.architecture()):
        threadNum = 1000
    else:
        threadNum = 500
    tpool = threadpool.ThreadPool(threadNum)
    requests = threadpool.makeRequests(runer, L)
    [tpool.putRequest(req) for req in requests]
    tpool.wait()


def master(itemsource):
    cpu_count = multiprocessing.cpu_count()
    ppool = Pool(processes=cpu_count) # set the process max number 3
    slice_itemsource = div_list(itemsource,cpu_count)
    itemsource = None
    for i in slice_itemsource:
        result = ppool.apply_async(threadworker,(i,))
    ppool.close()
    ppool.join()
    if result.successful():
        return True
    else:
        return False

def system():
    return platform.architecture()

def div_list(ls,n):
    ls_len = len(ls)
    if n> ls_len:
        return ls
    elif n == ls_len:
        return [[i] for i in ls]
    else:
        j = ls_len/n
        k = ls_len%n
        ls_return = []
        for i in xrange(0,(n-1)*j,j):
            ls_return.append(ls[i:i+j])
        ls_return.append(ls[(n-1)*j:])
        return ls_return




if __name__ == "__main__":
    start = time.time()
    master(range(1,2000))
    print(time.time()-start)






## window 32位系统最对可以开3000个线程 ，以此类推，64位系统应该最多可以开6000个线程，排除有部分线程被其他程序占用，部分线程需要预留，理论上，我可以使用系统50%的线程不会出现问题
