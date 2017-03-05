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

__version__ = "0.2.4"
__version_info__ = ( 0, 2, 4)




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





class _CmdRunObject(object):
    def __trans_to_string(self,s):
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

    def __enqueue_output(self,out, queue,description,endq):
        for line in iter(out.readline, b''):
            transline = self.__trans_to_string(line)
            transline = transline.rstrip('\r\n')
            queue.put(transline)
        endq.put('done')
        endq.task_done()
        return
    def __prepare_out(self):
        if self.__p.stdout is not None:
            if self.recvq is None:
                self.recvq = Queue.Queue()
            assert(self.endout is None)
            self.endout = Queue.Queue()
            assert(self.tout is None)
            self.tout = threading.Thread(target=self.__enqueue_output,args=(self.__p.stdout,self.recvq,'stdout',self.endout))
        return

    def __prepare_err(self):
        if self.__p.stderr is not None:
            if self.recvq is None:
                self.recvq = Queue.Queue()
            assert(self.enderr is None)
            self.enderr = Queue.Queue()
            assert(self.terr is None)
            self.terr = threading.Thread(target=self.__enqueue_output,args=(self.__p.stderr,self.recvq,'stderr',self.enderr))
        return

    def __start_out(self):
        if self.tout is not None:
            self.tout.start()
            self.outended = False
            logging.info('outended False')
        return

    def __start_err(self):
        if self.terr is not None:
            self.terr.start()
            self.errended = False
            logging.info('errended False')
        return

    def __init__(self,cmd,stdoutfile,stderrfile,shellmode,copyenv):
        self.__p = run_read_cmd(cmd,stdoutfile,stderrfile,shellmode,copyenv)
        self.terr = None
        self.tout = None
        self.endout = None
        self.outended = True
        self.errended = True
        self.recvq = None
        self.enderr = None
        self.endout = None
        self.__prepare_out()
        self.__prepare_err()
        self.__start_out()
        self.__start_err()
        self.__exitcode = 0
        return

    def __wait_err(self):
        if self.terr is not None:
            self.terr.join()
            self.terr = None
        return

    def __wait_out(self):
        if self.tout is not None:
            self.tout.join()
            self.tout = None

    def __wait_recvq(self):
        if self.recvq is not None:
            assert(self.recvq.empty())
            # nothing to be done
            self.recvq = None
        return

    def __get_exitcode(self):
        exitcode = self.__exitcode
        if self.__p is not None:
            while True:
                # wait 
                pret = self.__p.poll()
                if pret is not None:
                    exitcode = pret
                    logging.info('exitcode %d'%(exitcode))
                    break
                # wait for a time
                logging.info('will wait')
                time.sleep(0.1)
            if self.__p.stdout is not None:
                self.__p.stdout.close()
                self.__p.stdout = None
            if self.__p.stderr is not None:
                self.__p.stderr.close()
                self.__p.stderr = None
            self.__p = None
        self.__exitcode = exitcode
        return exitcode

    def call_readback(self,callback,ctx):
        if self.__p is None:
            return
        while True:
            if self.errended and self.outended:
                logging.info('outended errended')
                break
            try:
                rl = self.recvq.get_nowait()
                if callback is not None:
                    callback(rl,ctx)
            except Queue.Empty:
                if not self.errended:
                    try:
                        rl = self.enderr.get_nowait()
                        if rl == 'done':
                            logging.info('errended')
                            self.errended = True
                            self.enderr.join()
                            self.enderr = None
                    except Queue.Empty:
                        pass
                if not self.outended :
                    try:
                        rl = self.endout.get_nowait()
                        if rl == 'done':
                            logging.info('outended')
                            self.outended = True
                            self.endout.join()
                            self.endout = None
                    except Queue.Empty:
                        pass
                if not self.errended or not self.outended:
                    # sleep for a while to get 
                    time.sleep(0.1)
        return

    def __iter__(self):
        if self.__p is not None:
            while True:
                if self.errended and self.outended:
                    break
                try:
                    rl = self.recvq.get_nowait()
                    yield rl
                except Queue.Empty:
                    if not self.errended:
                        try:
                            rl = self.enderr.get_nowait()
                            if rl == 'done':
                                self.errended = True
                                self.enderr.join()
                                self.enderr = None
                        except Queue.Empty:
                            pass
                    if not self.outended :
                        try:
                            rl = self.endout.get_nowait()
                            if rl == 'done':
                                self.outended = True
                                self.endout.join()
                                self.endout = None
                        except Queue.Empty:
                            pass
                    if not self.errended or not self.outended:
                        # sleep for a while to get 
                        time.sleep(0.1)
            # all is ok ,so remove the resource
            self.__clean_resource()


    def __clean_resource(self):
        self.__wait_out()
        self.__wait_err()
        self.__wait_recvq()
        return self.__get_exitcode()

    def get_exitcode(self):
        return self.__clean_resource()

    def __del__(self):
        self.__clean_resource()
        return

def run_command_callback(cmd,callback,ctx,stdoutfile=subprocess.PIPE,stderrfile=None,shellmode=True,copyenv=None):
    cmdobj = _CmdRunObject(cmd,stdoutfile,stderrfile,shellmode,copyenv)
    cmdobj.call_readback(callback,ctx)
    return cmdobj.get_exitcode()


def run_cmd_output(cmd,stdout=True,stderr=False,shellmode=True,copyenv=None):
    if stdout:
        stdoutfile=subprocess.PIPE
    else:
        stdoutfile=open(os.devnull,'wb')

    if stderr:
        stderrfile=subprocess.PIPE
    else:
        stderrfile=open(os.devnull,'wb')
    return _CmdRunObject(cmd,stdoutfile,stderrfile,shellmode,copyenv)



