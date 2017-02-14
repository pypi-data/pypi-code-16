#!/usr/bin/python

import os
import sys
import subprocess
import logging
import time
import threading
try:
    import Queue
except ImportError:
    import queue as Queue

__version__ = "0.2.0"
__version_info__ = ( 0, 2, 0)




def run_cmd_wait(cmd,mustsucc=1,noout=1):
    logging.debug('run (%s)'%(cmd))
    if noout > 0:
        ret = subprocess.call(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    else:
        ret = subprocess.call(cmd,shell=True)
    if mustsucc and ret != 0:
        raise Exception('run cmd (%s) error'%(cmd))
    return ret

def run_read_cmd(cmd,stdoutfile=subprocess.PIPE,stderrfile=subprocess.PIPE,shellmode=True,copyenv=None):
    #logging.info('run %s stdoutfile %s stderrfile %s shellmode %s copyenv %s'%(cmd,stdoutfile,stderrfile,shellmode,copyenv))
    if copyenv is None:
        copyenv = os.environ.copy()
    cmds = cmd
    if isinstance(cmd,list):
        cmds = ''
        i = 0
        for c in cmd:
            if i > 0 :
                cmds += ' '
            cmds += '"%s"'%(c)
            i += 1
    p = subprocess.Popen(cmds,stdout=stdoutfile,stderr=stderrfile,shell=shellmode,env=copyenv)
    return p

def __trans_to_string(s):
    if sys.version[0] == '3':
        encodetype = ['UTF-8','latin-1']
        idx=0
        while idx < len(encodetype):
            try:
                return s.decode(encoding=encodetype[idx])
            except:
                idx += 1
        raise Exception('not valid bytes (%s)'%(repr(s)))
    return s


def __enqueue_output(out, queue,description,endq):
    for line in iter(out.readline, b''):
        transline = __trans_to_string(line)
        transline = transline.rstrip('\r\n')
        queue.put(transline)
    endq.put('done')
    endq.task_done()
    return

def run_command_callback(cmd,callback,ctx,stdoutfile=subprocess.PIPE,stderrfile=None,shellmode=True,copyenv=None):
    p = run_read_cmd(cmd,stdoutfile,stderrfile,shellmode,copyenv)
    terr = None
    tout = None
    endout = None
    enderr = None
    outended = True
    errended = True
    recvq = None

    if p.stdout is not None:
        if recvq is None:
            recvq = Queue.Queue()
        endout = Queue.Queue()
        tout = threading.Thread(target=__enqueue_output, args=(p.stdout, recvq,'stdout',endout))

    if p.stderr is not None:
        if recvq is None:
            recvq = Queue.Queue()
        enderr = Queue.Queue()
        terr = threading.Thread(target=__enqueue_output,args=(p.stderr,recvq,'stderr',enderr))

    if tout is not None:
        tout.start()
        outended = False

    if terr is not None:
        terr.start()
        errended = False

    exitcode = -1
    while True:
        if errended and outended:
            break
        try:
            rl = recvq.get_nowait()
            if callback is not None:
                callback(rl,ctx)
        except Queue.Empty:
            if not errended:
                try:
                    rl = enderr.get_nowait()
                    if rl == 'done':
                        errended = True
                        enderr.join()
                        enderr = None
                except Queue.Empty:
                    pass
            if not outended :
                try:
                    rl = endout.get_nowait()
                    if rl == 'done':
                        outended = True
                        endout.join()
                        endout = None
                except Queue.Empty:
                    pass
            if not errended or not outended:
                # sleep for a while to get 
                time.sleep(0.1)

    logging.info('over done')
    if terr is not None:
        logging.info('terr wait')
        terr.join()
        terr = None
        logging.info('terr done')
    if tout is not None:
        logging.info('tout wait')
        tout.join()
        tout = None
        logging.info('tout done')
    if recvq is not None:
        assert(recvq.empty())
        # nothing to be done
        recvq = None
        logging.info('recvq done')


    if p is not None:
        while True:
            # wait 
            pret = p.poll()
            if pret is not None:
                exitcode = pret
                logging.info('exitcode %d'%(exitcode))
                break
            # wait for a time
            logging.info('will wait')
            time.sleep(0.1)
        if p.stdout is not None:
            p.stdout.close()
            p.stdout = None
        if p.stderr is not None:
            p.stderr.close()
            p.stderr = None
        p = None
    return exitcode


