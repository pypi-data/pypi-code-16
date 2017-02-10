from __future__ import print_function
import time
import sys
import logging
import collections
import threading
import traceback
import os
import platform
import argparse
import requests
from datetime import datetime

from MeteorClient import MeteorClient
try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x
from subprocess import Popen, PIPE, STDOUT
from utils import NonBlockingStreamReader
from utils import rate_limited
from MeteorFiles import Uploader

RATE_LIMIT = 1 #s

class Task(object):

    def __init__(self, taskDoc, worker, meteorClient):
        self.taskDoc = taskDoc
        self.worker = worker
        self.meteorClient = meteorClient
        self.abort = threading.Event()
        self.has_key = self.taskDoc.has_key
        if self.taskDoc.has_key('_id'):
            self.id = self.taskDoc['_id']
        assert self.id
        self.widget = self.worker.get_registered_widget(self.get('widgetId'))
        assert self.widget
        if self.get('parent') is None or self.get('parent') == '':
            self.workdir = os.path.abspath(os.path.join(self.widget.workdir, 'task-'+self.id))
        else:
            self.workdir = os.path.abspath(os.path.join(self.widget.workdir, 'task-'+self.get('parent'), 'task-'+self.id))
        self.processor = None
        self.subtasks = set()

    def __getitem__(self, key):
        if not self.taskDoc:
            return None
        if '.' in key:
            ks = key.split('.')
            d = self.taskDoc
            for k in ks:
                if isinstance(d, dict) and d.has_key(k):
                    d = d[k]
                else:
                    return None
            return d
        elif self.taskDoc.has_key(key):
            return self.taskDoc[key]
        else:
            return None

    def __set__(self, key, value=None):
        assert (type(key) is str and not value is None)or (type(key) is dict and value is None)

        if not type(key) is dict and self.get(key) == value:
            return

        if type(key) is dict:
            vdict = key
            self.meteorClient.call('tasks.update.worker', [
                                   self.id, self.worker.id, self.worker.token, {'$set': vdict}])
            return

        if key == "visible2worker" and value == False:
            vdict = {key: value, "status.running": False, "status.waiting": False}
        # elif self.processor and (self.get('status.running') != self.processor.running or self.get('status.waiting') != self.processor.waiting):
        #     vdict = {key: value, "status.running": self.processor.running, "status.waiting": self.processor.waiting}
        else:
            vdict = {key: value}

        self.meteorClient.call('tasks.update.worker', [
                               self.id, self.worker.id, self.worker.token, {'$set': vdict}])
        # if key == 'running':
        #     if self.processor:
        #         self.processor.running = value
        #     return


    def __setitem__(self, key, value):
        return self.__set__(key,value)

    def get(self, key):
        return self.__getitem__(key)

    #@rate_limited(RATE_LIMIT, important=True)
    def set(self, key, value=None):
        self.__set__(key, value)

    #@rate_limited(RATE_LIMIT, important=False)
    def update(self, key, value=None):
        self.__set__(key, value)

    #@rate_limited(RATE_LIMIT, important=True)
    def push(self, key, value=None):
        try:
            vdict = key if type(key) is dict and value is None else {key: value}
            self.meteorClient.call('tasks.update.worker', [
                                   self.id, self.worker.id, self.worker.token, {'$push': vdict}])
        except Exception as e:
            print('error ocurred during setting ' + key)

    #@rate_limited(RATE_LIMIT, important=True)
    def pull(self, key, value=None):
        try:
            vdict = key if type(key) is dict and value is None else {key: value}
            self.meteorClient.call('tasks.update.worker', [
                                   self.id, self.worker.id, self.worker.token, {'$pull': vdict}])
        except Exception as e:
            print('error ocurred during setting ' + key)

    # TODO: get widget_code

    def upload(self, filePath, verbose=False):
        uploader = Uploader(self.meteorClient, 'files', transport='http', verbose=verbose)
        meta = {"taskId":self.id, "widgetId":self.get('widgetId'), "workerId":self.worker.id, 'workerToken': self.worker.token}
        # TODO: support relative path to task.workdir
        # TODO: also make a copy to worker.datadir for potential further usage
        uploader.upload(filePath, meta=meta)

    def file(self, fileId, timeout=10):
        self.__fetched = False
        self.__fileObj = None
        def callback(error, fileObject):
            self.__fetched = True
            if error:
                print(error)
            self.__fileObj = fileObject
        timeout_start = time.time()
        self.meteorClient.call('file.fetch.worker', [fileId, self.id, self.worker.id, self.worker.token], callback)
        while time.time() < timeout_start + timeout:
            if self.__fetched:
                break
            time.sleep(0.1)
        # print(time.time()-timeout_start)
        return self.__fileObj

    def download(self, file, use_cache=True, verbose=False):
        assert file, 'please provide a file id or a file object to download'
        if isinstance(file, (str, unicode)):
            fileObj = self.file(file)
            if fileObj:
                return self.download(fileObj, use_cache, verbose)
            else:
                return None
        else:
            fileObj = file

        if fileObj:
            baseurl = self.meteorClient.ddp_client.url
            assert baseurl.startswith('ws://') and baseurl.endswith('/websocket')
            if not fileObj.has_key('version'):
                fileObj['version'] = 'original'
            if fileObj.has_key('extension') and len(fileObj['extension'])>0:
                ext = '.' + fileObj['extension']
            else:
                ext = ''
            fileObj['ext'] = ext
            downloadUrl = 'http' + baseurl[2:-10] + "{_downloadRoute}/{_collectionName}/{_id}/{version}/#{_id}#{ext}".format(**fileObj)
            if not os.path.exists(self.workdir):
                os.makedirs(self.workdir)
            if verbose:
                print('downloading '+ downloadUrl)

            save_dir = os.path.join(self.worker.datadir, fileObj['_id'])
            save_path = os.path.join(save_dir, fileObj['name'])

            if use_cache:
                if os.path.exists(save_path):
                    statinfo = os.stat(save_path)
                    if statinfo.st_size == fileObj['size']:
                        if verbose:
                            print('use cached file from '+ save_path)
                        return save_path


            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            r = requests.get(downloadUrl, stream=True)
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
                        if verbose:
                            print('.', end='')
            if verbose:
                print('saved to '+ save_path)
            return save_path

    def find(self, collection, selector={}):
        '''
        support multi-level selector
        '''
        results = []
        if isinstance(collection, str):
            collection_items = self.meteorClient.collection_data.data.get(collection, {}).items()
        elif isinstance(collection, list):
            collection_items = [(doc['_id'],doc) for doc in collection]
        else:
            raise Exception('unsupported collection type')
        for _id, doc in collection_items:
            doc.update({'_id': _id})
            if selector == {}:
                results.append(doc)
            for key, value in selector.items():
                if '.' in key:
                    keys = key.split('.')
                    v = doc
                    for k in keys:
                        if k in v:
                            v = v[k]
                        else:
                            break
                    if v == value:
                        results.append(doc)
                else:
                    if isinstance(value, dict):
                        if value.has_key('$in') and isinstance(value['$in'], list):
                            if doc[key] in value['$in']:
                                results.append(doc)
                                break
                    elif key in doc and doc[key] == value:
                        results.append(doc)

        return results

    def find_one(self, collection, selector={}):
        if isinstance(collection, str):
            collection_items = self.meteorClient.collection_data.data.get(collection, {}).items()
        elif isinstance(collection, list):
            collection_items = [(doc['_id'],doc) for doc in collection]
        else:
            raise Exception('unsupported collection type')
        for _id, doc in collection_items:
            doc.update({'_id': _id})
            if selector == {}:
                return doc
            for key, value in selector.items():
                if '.' in key:
                    keys = key.split('.')
                    v = doc
                    for k in keys:
                        if k in v:
                            v = v[k]
                        else:
                            break
                    if v == value:
                        return doc
                else:
                    if isinstance(value, dict):
                        if value.has_key('$in') and isinstance(value['$in'], dict):
                            for k in value['$in']:
                                if doc[k] in value['$in'][k]:
                                    return doc
                    elif key in doc and doc[key] == value:
                        return doc

    def save(self, filename=None):
        import ejson
        if not os.path.exists(self.workdir):
            os.makedirs(self.workdir)
        if filename is None:
            filename = 'task.ejson'
        with open(os.path.join(self.workdir, filename), 'w') as f:
            f.write(ejson.dumps(self.taskDoc))

class Widget(object):

    def __init__(self, widgetDoc, worker, meteorClient):
        self.widgetDoc = widgetDoc
        self.meteorClient = meteorClient
        self.worker = worker
        self.has_key = self.widgetDoc.has_key
        if self.widgetDoc.has_key('_id'):
            self.id = self.widgetDoc['_id']
        else:
            raise Exception('invalid widgetDoc')
        self.workdir = os.path.join(self.worker.workdir, 'widget-'+self.id)
        if not os.path.exists(self.workdir):
            os.makedirs(self.workdir)

    def __getitem__(self, key):
        if not self.widgetDoc:
            return None
        if '.' in key:
            ks = key.split('.')
            d = self.widgetDoc
            for k in ks:
                if isinstance(d, dict) and d.has_key(k):
                    d = d[k]
                else:
                    return None
            return d
        elif self.widgetDoc.has_key(key):
            return self.widgetDoc[key]
        else:
            return None

    def __setitem__(self, key, value):
        # TODO: remove this after login
        raise Exception('widgets is readonly for worker.')

    def get(self, key):
        return self.__getitem__(key)

    #@rate_limited(RATE_LIMIT, important=True)
    def set(self, key, value):
        self.__setitem__(key, value)

    #@rate_limited(RATE_LIMIT, important=False)
    def update(self, key, value):
        self.__setitem__(key, value)

    def exec_widget_task_processor(self, task, widget, worker):
        import time
        id = widget.id
        widget_task_processor = self.default_task_processor
        ns = {'TASK': task, 'WIDGET': widget,
              'WORKER': worker, '__name__': '__worker__', 'time': time}
        if widget.get('code_snippets').has_key('__init___py'):
            exec(widget.get('code_snippets')['__init___py']['content'], ns)
        if ns.has_key('TASK_PROCESSOR'):
            return ns['TASK_PROCESSOR']
        else:
            return None

    def default_task_processor(self, task, widget, worker):
        print('default_task_processor: ' + task.id)

    def get_task_processor(self):
        return self.exec_widget_task_processor


class Worker(object):

    def __init__(self, worker_id=None, worker_token=None,
                 server_url='ws://localhost:3000/websocket', workdir='./', dev_mode=True, thread_num=10, datadir=None):
        self.serverUrl = server_url
        self.id = worker_id
        assert not worker_id is None, 'Please set a valid worker id and token.'
        self.token = worker_token
        self.devWidgets = {}
        self.productionWidgets = {}
        self.workerDoc = None
        self.userName = None
        self.userId = None
        self.workTasks = collections.OrderedDict()
        self.taskQueue = Queue()
        self.thread_num = thread_num
        self.maxTaskNum = 50
        self.taskWorkerThreads = []
        self.taskWorkerAbortEvents = []
        self.resources = {}

        from . import __version__
        self.workerVersion = __version__ or 'UNKNOWN'

        print('worker version: '+str(__version__))

        self.logger = logging.getLogger('worker')

        self.workdir = os.path.abspath(os.path.join(workdir, 'worker-'+worker_id))
        if not os.path.exists(self.workdir):
            os.makedirs(self.workdir)

        if datadir is None:
            datadir = os.path.join(workdir, 'data')

        self.datadir = os.path.abspath(datadir)
        if not os.path.exists(self.datadir):
            os.makedirs(self.datadir)

        self.init()
        self.get_system_info()
        try:
            self.get_gpu_info()
        except Exception as e:
            print('gpu info is not available.')
        self.connectionManager = ConnectionManager(
            server_url=server_url, worker=self)
        self.meteorClient = self.connectionManager.client

    def start(self):
        self.start_monitor_thread()
        self.start_task_threads()
        self.connectionManager.connect()
        self.connectionManager.run()

    def init(self):
        pass

    def get_system_info(self):
        self.resources['platform'] ={
            'uname': ', '.join(platform.uname()),
            'machine':  platform.machine(),
            'system': platform.system(),
            'processor': platform.processor(),
            'node': platform.node()}
        try:
            from sh import which
            exe_checklist = ['nvcc', 'java', 'lua', 'qstat', 'squeue', 'python']
            self.resources['exe'] = {}
            for e in exe_checklist:
                self.resources['exe'][e] = which(e)

        except Exception as e:
            raise

        self.update_system_info()

    def update_system_info(self):
        self.resources['date_time'] =  datetime.now().strftime("%b %d %H:%M:%S")

    def get_gpu_info(self):
        from device_query import get_devices, get_nvml_info
        devices = get_devices()
        if not self.resources.has_key('gpu'):
            self.resources['gpu'] = {}
        gpus = self.resources['gpu']
        for i, device in enumerate(devices):
            if not gpus.has_key('gpu' + str(i)):
                gpus['gpu' + str(i)] = {}
            gpuInfo = gpus['gpu' + str(i)]
            for name, t in device._fields_:
                if name not in [
                        'name', 'totalGlobalMem', 'clockRate', 'major', 'minor', ]:
                    continue
                if 'c_int_Array' in t.__name__:
                    val = ','.join(str(v) for v in getattr(device, name))
                else:
                    val = getattr(device, name)
                gpuInfo[name] = val

        self.update_gpu_info()

    def update_gpu_info(self):
        from device_query import get_devices, get_nvml_info
        devices = get_devices()
        if not self.resources.has_key('gpu'):
            self.resources['gpu'] = {}
        gpus = self.resources['gpu']
        for i, device in enumerate(devices):
            if not gpus.has_key('gpu' + str(i)):
                gpus['gpu' + str(i)] = {}
            gpuInfo = gpus['gpu' + str(i)]
            info = get_nvml_info(i)
            if info is not None:
                if 'memory' in info:
                    gpuInfo['total_memory'] = info['memory']['total']
                    gpuInfo['used_memory'] = info['memory']['used']
                if 'utilization' in info:
                    gpuInfo['memory_utilization'] = info['utilization']['memory']
                    gpuInfo['gpu_utilization'] = info['utilization']['gpu']
                if 'temperature' in info:
                    gpuInfo['temperature'] = info['temperature']

    def worker_monitor(self):
        while not self.connectionManager.ready:
            time.sleep(0.2)
        print('worker monitor thread started.')
        self.get_system_info()
        self.get_gpu_info()
        self.set('version', self.workerVersion)
        self.set('name', self.resources['platform']['node'] + '-' + self.id)
        self.set('status', 'ready')
        while True:
            self.update_system_info()
            try:
                self.update_gpu_info()
            except Exception as e:
                pass
            self.set('resources', self.resources)
            time.sleep(2.0)

    def register_widget(self, widget):
        id = widget.id
        print('register widget: ' + id)
        if widget.get('mode') == 'development':
            self.devWidgets[id] = widget
            if self.productionWidgets.has_key(id):
                del self.productionWidgets[id]
            if widget.get('code_snippets'):
                for k in widget.get('code_snippets').keys():
                    k = k.replace('.', '_')
                    code = widget.get('code_snippets')[k]
                    with open(os.path.join(widget.workdir, code['name']), 'w') as f:
                        f.write(code['content'])

        if widget.get('mode') == 'production':
            self.productionWidgets[id] = widget
            if self.devWidgets.has_key(id):
                del self.devWidgets[id]

    def unregister_widget(self, widgetId):
        if self.devWidgets.has_key(widgetId):
            del self.devWidgets[widgetId]
        if self.productionWidgets.has_key(widgetId):
            del self.productionWidgets[widgetId]

    def is_widget_registered(self, widgetId):
        if self.devWidgets.has_key(widgetId):
            return True
        if self.productionWidgets.has_key(widgetId):
            return True
        return False

    def get_registered_widget(self, widgetId):
        if self.devWidgets.has_key(widgetId):
            return self.devWidgets[widgetId]
        if self.productionWidgets.has_key(widgetId):
            return self.productionWidgets[widgetId]
        return None

    def __getitem__(self, key):
        if not self.workerDoc:
            return None
        if '.' in key:
            ks = key.split('.')
            d = self.workerDoc
            for k in ks:
                if d.has_key(k):
                    d = d[k]
                else:
                    return None
            return d
        elif self.workerDoc.has_key(key):
            return self.workerDoc[key]
        else:
            return None

    def __set__(self, key, value=None):
        assert (type(key) is str and not value is None)or (type(key) is dict and value is None)
        if not type(key) is dict and self.get(key) == value:
            return
        try:
            vdict = key if type(key) is dict and value is None else {key: value}
            self.meteorClient.call('workers.update', [self.id, self.token, {
                                   '$set': vdict}], self.default_update_callback)
        except Exception as e:

            print('error ocurred during setting ' + key)
    def __setitem__(self, key, value):
        self.__set__(key, value)

    def get(self, key):
        return self.__getitem__(key)

    #@rate_limited(RATE_LIMIT)
    def set(self, key, value=None):
        self.__set__(key, value)

    #@rate_limited(RATE_LIMIT, important=False)
    def update(self, key, value=None):
        self.__set__(key, value)

    #@rate_limited(RATE_LIMIT)
    def push(self, key, value):
        try:
            self.meteorClient.call('workers.update', [self.id, self.token, {
                                   '$push': {key: value}}], self.default_update_callback)
        except Exception as e:
            print('error ocurred during setting ' + key)

    #@rate_limited(RATE_LIMIT)
    def pull(self, key, value):
        try:
            self.meteorClient.call('workers.update', [self.id, self.token, {
                                   '$pull': {key: value}}], self.default_update_callback)
        except Exception as e:
            print('error ocurred during setting ' + key)

    def default_update_callback(self, error, result):
        if error:
            print(error)
            return

    def start_monitor_thread(self):
        mThread = threading.Thread(target=self.worker_monitor)
        # daemon lets the program end once the tasks are done
        mThread.daemon = True
        mThread.start()
        self.monitorThread = mThread

    def start_task_threads(self):
        for i in range(self.thread_num):
            abortEvent = threading.Event()
            # Create 1 threads to run our jobs
            aThread = threading.Thread(
                target=self.work_on_task, args=[abortEvent])
            # daemon lets the program end once the tasks are done
            aThread.daemon = True
            aThread.start()
            self.taskWorkerThreads.append(aThread)
            self.taskWorkerAbortEvents.append(abortEvent)
        print('{} task threads started'.format(self.thread_num))

    def stop_task_threads(self):
        for abortEvent in self.taskWorkerAbortEvents:
            abortEvent.set()
        print('stop worker')
        self.taskWorkerThreads = []
        self.taskWorkerAbortEvents = []

    def task_worker_changed(self, task, key, value):
        print('worker changed')
        if value != self.id:
            self.remove_task(task)

    def add_task(self, task):
        taskId = task.id
        if task and task.get('widgetId') and self.is_widget_registered(task.get('widgetId')):
            widget = self.get_registered_widget(task.get('widgetId'))
            task_processor = widget.get_task_processor()
            if task_processor:
                try:
                    #task.set('status', {"stage":'-', "running": False, "error":'', "progress":-1})
                    if not 'autoRestart' in task.get('tags') and (task.get('status.running') or task.get('status.waiting')):
                        raise Exception('worker restarted unexpectedly.')
                    if 'ing' in task.get('status.stage'):
                        task.set('status.stage', '-')
                    if task.get('cmd') == '':
                        raise Exception('no command available.')
                    tp = task_processor(task, widget, self)
                except Exception as e:
                    traceback.print_exc()
                    task.set('status', task.get('status') or {})
                    task.set('status.running', False)
                    task.set('status.waiting', False)
                    task.set('status.error', traceback.format_exc())
                    task.set('cmd', '')
                    task.set('visible2worker', False)
                else:
                    if tp:
                        if not self.workTasks.has_key(taskId):
                            #print('add task {} to {}'.format(taskId, self.id))
                            if not task.get('parent'):
                                self.workTasks[taskId] = task
                                for t in self.workTasks.values():
                                    if t.get('parent') == task.id:
                                        task.subtasks.add(t)
                                        if t.processor and (t.processor.running or t.processor.waiting):
                                            if not task.get('cmd') or task.get('cmd') == '':
                                                task.set('cmd','run')
                            elif self.workTasks.has_key(task.get('parent')):
                                self.workTasks[taskId] = task
                                self.workTasks[task.get('parent')].subtasks.add(task)
                            else:
                                task.set('status.stage', 'ignored')
                                task.set('status.error', 'parent task is not in the available to worker')
                                task.set('visible2worker', False)
                                print('ignore task {}/{}, disable it from worker'.format(task.get('name'), task.id))
                    else:
                        task.set('status.error', 'no task processor defined.')
                        task.set('visible2worker', False)
                        return None
                if self.workTasks.has_key(taskId):
                    self.execute_task_cmd(
                        self.workTasks[taskId], 'cmd', task.get('cmd'))
                    # if task.get('cmd') == 'run':
                    #    self.run_task(self.workTasks[taskId])
                    return self.workTasks[taskId]
            else:
                print('widget task processor is not available.')
        else:
            if task:
                task.set('visible2worker', False)
            print("widget is not registered: taskid=" + taskId)

    def remove_task(self, task):
        if isinstance(task, str):
            return
        if self.workTasks.has_key(task.id):
            task = self.workTasks[task.id]
            if task.processor.running or task.processor.waiting:
                task.processor.stop()
            # remove this task from parent task
            if task.get('parent') and self.workTasks.has_key(task.get('parent')):
                if task in self.workTasks[task.get('parent')].subtasks:
                    self.workTasks[task.get('parent')].subtasks.remove(task)

            del self.workTasks[task.id]
            print('remove task {} from widget {}'.format(task.id, self.id))

    def execute_task_cmd(self, task, key, cmd):
        self.set('cmd', '')
        if cmd == 'run':
            print('---run task---')
            self.run_task(task)
        if cmd == 'show':
            print('--show task--')
            task.set('cmd', '')
        elif cmd == 'stop':
            print('---stop task---')
            self.stop_task(task)

    def execute_worker_cmd(self, cmd):
        self.set('cmd', '')
        if cmd == 'run':
            self.start_task_threads()
        elif cmd == 'stop':
            self.stop_task_threads()

    def run_task(self, task):
        id = task.id
        if self.workTasks.has_key(id):
            task.set('status.waiting', True)
            task.processor.waiting = True
            task.set('status.stage', 'queued')
            print('task Qsize:' + str(self.taskQueue.qsize()))
            self.taskQueue.put(id)

    def stop_task(self, task):
        id = task.id
        if self.workTasks.has_key(id):
            if self.workTasks[id].processor.running or self.workTasks[id].processor.waiting:
                self.workTasks[id].processor.stop()

    def work_on_task(self, abortEvent):
        import time
        # print('working thread for tasks of widget {} started'.format(self.id))
        while True:
            if abortEvent.is_set():
                break
            try:
                taskId = self.taskQueue.get()
                if self.get('status') != 'running':
                    self.set('status', 'running')
                if self.workTasks.has_key(taskId):
                    task = self.workTasks[taskId]
                    if task.processor and task.processor.waiting:
                        if not task.get('parent'):
                            task.processor.start()
                            while task.processor.running:
                                time.sleep(0.1)
                        elif task.get('parent') and self.workTasks.has_key(task.get('parent')):
                            ptask = self.workTasks[task.get('parent')]
                            if ptask.processor and not ptask.processor.running:
                                task.set('status.stage', 'waiting')
                                ptask.processor.start()
                            task.processor.start()
                            while task.processor.running:
                                time.sleep(0.1)
                        else:
                            task.processor.waiting = False
                            task.set('status.waiting', False)
                            task.set('status.stage', 'ignored')
                            task.set('status.error', 'parent task is not in the available to worker')
                            task.set('visible2worker', False)
                            print('ignore task {}/{}, disable it from worker'.format(task.get('name'), task.id))
                            # task.processor.start()
                self.taskQueue.task_done()

            except Empty:
                self.set('status', 'ready')
                time.sleep(1)
            except:
                traceback.print_exc()
            time.sleep(0.5)

        print('working thread for {} stopped'.format(self.id))

    def stop(self):
        try:
            for task in self.workTasks:
                if task.processor.running or task.processor.waiting :
                    task.processor.stop()
        except Exception as e:
            pass
        self.set('status', 'stopped')
        for subscription in self.meteorClient.subscriptions.copy():
            self.meteorClient.unsubscribe(subscription)

class ConnectionManager():

    def __init__(self, server_url='ws://localhost:3000/websocket', worker=None):
        self.server_url = server_url
        self.client = MeteorClient(server_url)
        self.client.on('subscribed', self.subscribed)
        self.client.on('unsubscribed', self.unsubscribed)
        self.client.on('added', self.added)
        self.client.on('changed', self.changed)
        self.client.on('removed', self.removed)
        self.client.on('connected', self.connected)
        self.client.on('logged_in', self.logged_in)
        self.client.on('logged_out', self.logged_out)
        self.worker = worker
        self.connected = False
        self.ready = False

    def connect(self):
        self.client.connect()

    def connected(self):
        self.connected = True
        print('connected to ' + self.server_url)
        #self.client.login('test', '*****')
        if not 'workers.worker' in self.client.subscriptions:
            self.client.subscribe(
                'workers.worker', [self.worker.id, self.worker.token])

    def logged_in(self, data):
        self.userId = data['id']
        print('* LOGGED IN {}'.format(data))

    def subscribed(self, subscription):
        print('* SUBSCRIBED {}'.format(subscription))
        self.ready = True
        if subscription == 'workers.worker':
            if self.client.find_one('workers', selector={'_id': self.worker.id}):
                print('-----Worker {} found-----'.format(self.worker.id))
                if not 'widgets.worker' in self.client.subscriptions:
                    self.client.subscribe(
                        'widgets.worker', [self.worker.id, self.worker.token])
            else:
                raise Exception('Failed to find the worker with id:{} token{}'.format(
                    self.worker.id, self.worker.token))

        if subscription == 'widgets.worker':
            print('widgets of this worker SUBSCRIBED-')

        elif subscription == 'tasks.worker':
            print('* tasks of this worker SUBSCRIBED-')

    def added(self, collection, id, fields):
        print('* ADDED {} {}'.format(collection, id))
        # for key, value in fields.items():
        #    print('  - FIELD {} {}'.format(key, value))
        if collection == 'tasks':
            if not self.worker.workTasks.has_key(id):
                if fields.has_key('worker') and fields['worker'] == self.worker.id:
                    taskDoc = self.client.find_one('tasks', selector={'_id': id})
                    widget = self.worker.get_registered_widget(taskDoc['widgetId'])
                    if widget:
                        task = Task(taskDoc, self.worker, self.client)
                        if task and task.id:
                            self.worker.add_task(task)
                        else:
                            # remove task if widget is not registered
                            self.client.call('tasks.update.worker', [
                                                   id, self.worker.id, self.worker.token, {'$set': {'visible2worker': False}}])
                    else:
                        # remove task if widget is not registered
                        self.client.call('tasks.update.worker', [
                                               id, self.worker.id, self.worker.token, {'$set': {'visible2worker': False}}])

        elif collection == 'users':
            self.userName = fields['username']
        elif collection == 'widgets':
            # widget = fields#self.client.find_one('widgets', selector={'name':
            widget_ = Widget(self.client.find_one(
                'widgets', selector={'_id': id}), self.worker, self.client)
            if widget_.id:
                self.worker.register_widget(widget_)
                if not 'tasks.worker' in self.client.subscriptions:
                    self.client.subscribe(
                        'tasks.worker', [self.worker.id, self.worker.token])

    def changed(self, collection, id, fields, cleared):
        #print('* CHANGED {} {}'.format(collection, id))
        # for key, value in fields.items():
        #    print('  - FIELD {} {}'.format(key, value))
        # for key, value in cleared.items():
        #    print('  - CLEARED {} {}'.format(key, value))
        if collection == 'tasks':
            if self.worker.workTasks.has_key(id):
                task = self.worker.workTasks[id]
                for key, value in fields.items():
                    if key == 'cmd':
                        self.worker.execute_task_cmd(task, key, value)
                    elif key == 'worker':
                        self.worker.task_worker_changed(task, key, value)

                    if task.processor.changeCallbackDict.has_key(key):
                        for changeCallback in task.processor.changeCallbackDict[key]:
                            try:
                                changeCallback(task, key, value)
                            except Exception as e:
                                traceback.print_exc()
                                task.set('status.error', traceback.format_exc())

                for key, value in cleared.items():
                    if key == 'cmd':
                        self.worker.execute_task_cmd(task, key, value)
                    elif key == 'worker':
                        self.worker.task_worker_changed(task, key, value)

                    if task.processor.changeCallbackDict.has_key(key):
                        for changeCallback in task.processor.changeCallbackDict[key]:
                            try:
                                changeCallback(task, key, value)
                            except Exception as e:
                                traceback.print_exc()
                                task.set('status.error', traceback.format_exc())

            else:
                if fields.has_key('worker') and fields['worker'] == self.worker.id:
                    self.worker.add_task(id)

                #print('task is not in worktask list: ' + id)
        if collection == 'widgets':
            widget_ = Widget(self.client.find_one(
                'widgets', selector={'_id': id}), self.worker, self.client)
            if widget_.id:
                self.worker.register_widget(widget_)

            if fields.has_key('workers'):
                if fields['workers'].has_key(self.worker.id):
                    #print('worker config changed')
                    worker = fields['workers'][self.worker.id]
                    if worker.has_key('cmd'):
                        self.worker.execute_worker_cmd(worker['cmd'])

    def removed(self, collection, id):
        print('* REMOVED {} {}'.format(collection, id))
        if collection == 'tasks':
            if self.worker.workTasks.has_key(id):
                task = self.worker.workTasks[id]
                self.worker.remove_task(task)
                for cb in task.processor.removeCallbackList:
                    cb(task)

    def unsubscribed(self, subscription):
        print('* UNSUBSCRIBED {}'.format(subscription))

    def logged_out():
        self.userId = None
        print('* LOGGED OUT')

    def subscription_callback(self, error):
        if error:
            print(error)

    def run(self):
        # (sort of) hacky way to keep the client alive
        # ctrl + c to kill the script
        try:
            while True:
                time.sleep(1)
        except:
            traceback.print_exc()
        finally:
            self.stop()
            print('server exited')

    def stop(self):
        try:
            for task in self.worker.workTasks:
                if task.processor:
                    task.processor.stop()
        except Exception as e:
            pass
        self.worker['status'] = 'stopped'
        for subscription in self.client.subscriptions.copy():
            self.client.unsubscribe(subscription)


if __name__ == '__main__':
    '''
    python dsWorker.py --workdir ./workdir --dev --server-url ws://localhost:3000/websocket --worker-id Xkzx4atx6auuxXGfX --worker-token qjygopwdoqvqkzu
    '''
    parser = argparse.ArgumentParser(description='distributed worker')
    parser.add_argument('--worker-id', dest='worker_id',
                        type=str, default='', help='id of the worker')
    parser.add_argument('--thread-num', dest='thread_num',
                        type=int, default=10, help='number of thread for the worker')
    parser.add_argument('--worker-token', dest='worker_token',
                        type=str, default='', help='token of the worker')
    parser.add_argument('--server-url', dest='server_url', type=str,
                        default='wss://ai.pasteur.fr/websocket', help='server url')
    parser.add_argument('--workdir', dest='workdir', type=str,
                        default='./workdir', help='workdir')
    parser.add_argument('--dev-mode', dest='dev_mode',
                        action='store_true', help='enable development mode')
    parser.add_argument('--verbose', dest='verbose',
                        action='store_true', help='enable debug logging')
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    dw = Worker(worker_id=args.worker_id, worker_token=args.worker_token, server_url=args.server_url,
                workdir=args.workdir, dev_mode=args.dev_mode, thread_num=args.thread_num)
    dw.start()
