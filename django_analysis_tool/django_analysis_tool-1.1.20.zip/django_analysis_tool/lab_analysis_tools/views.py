#coding:utf-8
import os,sys,logging
import tempfile
import zipfile
import time
import thread
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from base.workflow import Detect, unzipSource, DetectUnzip
import base
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from .forms import JsonForm
import json,csv,pickle
from lab.settings import JSON_ROOT,PROJECT_ROOT
from .models import Task,TaskDevice,Problem,TaskUnzip,SuConnectedTimedOut, NotFoundResultZip
from templatetags import poll_extras
import sqlite3
# import pandas as pd
from django.views.decorators.cache import cache_page
# from .visualize import SuTimedOut,SuTimedOutProportionPercentage,SuTimedOutStability, SuTimedOutSearchByDevice, \
#     NotFoundResultZipV
from base.utility.construct import DotableDict, JsonConfig
from base.scanner import *
import django.core.files


class Run(object):

    def __init__(self,detect):
        global unzipResult
        self.SEPARATOR = "|"
        self.detect = detect

    def _devicesCompare(self,cur_problem_devices,pro_task_id):
        '''
        :param cur_problem_devices:
        :param pro_task_id:
        :return: repr_repeat_devices, repr_unstable_devices, repr_newbird_devices
        '''
        repr_pro_all_devices = SuConnectedTimedOut.objects.get(task = Task.objects.get(task_id = pro_task_id)).all_devices
        repr_pro_problem_devices = SuConnectedTimedOut.objects.get(task = Task.objects.get(task_id = pro_task_id)).timedout_devices

        pro_all_devices = repr_pro_all_devices.split(self.SEPARATOR)
        pro_problem_devices = repr_pro_problem_devices.split(self.SEPARATOR)
        repeat_devices,unstable_devices,newbird_devices = [],[],[]
        for device_name in (device.name for device in cur_problem_devices):
            if device_name not in pro_all_devices: # 本次错误设备不在上次所有设备中
                newbird_devices.append(device_name)
            elif device_name in pro_problem_devices: # 本次错误设备在上次问题设备中
                repeat_devices.append(device_name)
            else:
                unstable_devices.append(device_name) # 本次错误设备不在上次问题设备中
        repr_repeat_devices = self.SEPARATOR.join(repeat_devices)
        repr_unstable_devices = self.SEPARATOR.join(unstable_devices)
        repr_newbird_devices = self.SEPARATOR.join(newbird_devices)

        return repr_repeat_devices, repr_unstable_devices, repr_newbird_devices


    # def _insert_SuConnectedTimedOut(self):
    #     task = Task.objects.get(task_id = self.unzipResult.task_id)
    #     all_devices = TaskDevice.objects.filter(task = task)
    #     repr_all_devices = self.SEPARATOR.join((device.name for device in all_devices))
    #     try:
    #         tmp_problem = Problem.objects.get(name = 'SU_CONNECTION_TIMEOUT')
    #         timedout_devices = all_devices.filter(problems = tmp_problem)
    #         repr_timedout_devices = self.SEPARATOR.join((device.name for device in timedout_devices))
    #     except:
    #         #没有su连接超时的模型对象，说明之前没有遇到过此问题
    #         timedout_devices = []
    #         repr_timedout_devices = ''
    #     if repr_timedout_devices == '':
    #         rate = float(0)
    #     else:
    #         rate = float(len(repr_timedout_devices.split(self.SEPARATOR)))/float(len(all_devices))
    #
    #     sqlite3_path = os.path.join(os.path.dirname(PROJECT_ROOT),'db.sqlite3')
    #     with sqlite3.connect(sqlite3_path) as con:
    #         df = pd.read_sql_query("SELECT * from lab_analysis_tools_task", con)
    #
    #     df_sort_index = df.set_index(df.task_id).sort_index()
    #     df_filter_task_id = df_sort_index[df_sort_index.task_id < self.unzipResult.task_id]
    #     try:
    #         pro_task_id = df_filter_task_id.iloc[-1].task_id
    #         repr_repeat_devices, repr_unstable_devices, repr_newbird_devices = self._devicesCompare(timedout_devices,pro_task_id)
    #     except IndexError:
    #         # 没有比当前task_id更早的任务
    #         repr_newbird_devices = repr_timedout_devices
    #         repr_repeat_devices, repr_unstable_devices = '',''
    #     SuConnectedTimedOut(task = task,
    #                         tid = self.unzipResult.task_id,
    #                         all_devices = repr_all_devices,
    #                         timedout_devices = repr_timedout_devices,
    #                         rate = rate,
    #                         repeat_devices = repr_repeat_devices,
    #                         unstable_devices = repr_unstable_devices,
    #                         newbird_devices = repr_newbird_devices).save()

    def insertUnzip(self,task_id):
        try:
            Task.objects.get(task_id = task_id).delete()
        except:
            pass
        finally:
            try:
                Task(task_id=task_id).save()
                devices = self.detect.devices
                for device_info in devices: #device_info 对应TaskDevice模型
                    dot = DotableDict(device_info) #使用dotableDict 封装每个设备信息，方便后续点号操作符处理
                    task = Task.objects.get(task_id = task_id)
                    # problem_list = []
                    # for key,value in device_info.items(): #key 对应Problem模型
                    #     if value == 'fail':
                    #         tmpObject = None
                    #         #如果发现字段值为'fail' ，说明此字段被标记为失败，应该为TaskDevice插入对应的Problem模型对象
                    #         try:
                    #             tmpObject = Problem.objects.get(name = key)
                    #         except:
                    #             #查找Problem对象抛出异常说明没有创建过该对象
                    #             tmpObject = Problem(name = key)
                    #             tmpObject.save()
                    #         finally:
                    #             problem_list.append(tmpObject)
                    taskDevice1 = TaskDevice(name=dot.device, task=task, result=dot.result, fail_detail=dot.fail_detail, solution=dot.solution)
                    taskDevice1.save()
                    # taskDevice1.problems.add(*problem_list)
            except:
                return HttpResponseRedirect(reverse('index'))


    def insert(self):

        try: #尝试删除与当前解压任务task_id相同的数据库task_id

            # Task.objects.get(task_id = unzipResult.task_id)

            Task.objects.get(task_id = unzipResult.task_id).delete()
        except:
            pass
        finally: # 执行数据库插入流程
            try:
                Task(task_id=unzipResult.task_id).save()
                #向TaskDevice模型中插入数据
                devices = self.detect.devices
                for device_info in devices: #device_info 对应TaskDevice模型
                    dot = DotableDict(device_info) #使用dotableDict 封装每个设备信息，方便后续点号操作符处理
                    task = Task.objects.get(task_id = unzipResult.task_id)
                    problem_list = []
                    for key,value in device_info.items(): #key 对应Problem模型
                        if value == 'fail':
                            tmpObject = None
                            #如果发现字段值为'fail' ，说明此字段被标记为失败，应该为TaskDevice插入对应的Problem模型对象
                            try:
                                tmpObject = Problem.objects.get(name = key)
                            except:
                                #查找Problem对象抛出异常说明没有创建过该对象
                                tmpObject = Problem(name = key)
                                tmpObject.save()
                            finally:
                                problem_list.append(tmpObject)
                    taskDevice1 = TaskDevice(name=dot.device, task=task, result=dot.result, fail_detail=dot.fail_detail, solution=dot.solution)
                    taskDevice1.save()
                    taskDevice1.problems.add(*problem_list)

                TaskUnzip(task = Task.objects.get(task_id = unzipResult.task_id),
                          zipfile_num = unzipResult.zipfile['num'],
                          zipfile_comment = unzipResult.zipfile['comment'],
                          zipfile_device = unzipResult.zipfile['device'],
                          valid_zipfile_num = unzipResult.valid_zipfile['num'],
                          valid_zipfile_comment = unzipResult.valid_zipfile['comment'],
                          valid_zipfile_device = unzipResult.valid_zipfile['device'],
                          resultzip_num = unzipResult.resultzip['num'],
                          resultzip_comment = unzipResult.resultzip['comment'],
                          resultzip_device = unzipResult.resultzip['device'],
                          valid_resultzip_num = unzipResult.valid_resultzip['num'],
                          valid_resultzip_comment = unzipResult.valid_resultzip['comment'],
                          valid_resultzip_device = unzipResult.valid_resultzip['device']).save()
            except:
                return HttpResponseRedirect(reverse('index'))



            # self._insert_SuConnectedTimedOut()

    def insert_luaunit(self):
        try: #尝试获取task_id ，以此判断是否需要执行插入流程
            Task.objects.get(task_id = self.unzipResult.task_id)
        except: # 无Task模型的task_id对应，则执行插入流程
            devices = self.detect.getLuaUnitDevices()
            Task(task_id = self.unzipResult.task_id).save()
            #向TaskDevice模型中插入数据
            for device_info in devices: #device_info 对应TaskDevice模型
                name = device_info.pop('device')
                luaunit_fail = device_info.pop('luaunit_fail')
                luaunit_pass = device_info.pop('luaunit_pass')
                fail_detail = device_info.pop('fail_detail')
                task = Task.objects.get(task_id = self.unzipResult.task_id)
                taskDevice1 = TaskDevice(name=name, task=task, result='', fail_detail=fail_detail, luaunit_fail=luaunit_fail, luaunit_pass=luaunit_pass)
                taskDevice1.save()
            TaskUnzip(task = Task.objects.get(task_id = self.unzipResult.task_id),
                      zipfile_num = self.unzipResult.zipfile['num'],
                      zipfile_comment = self.unzipResult.zipfile['comment'],
                      zipfile_device = self.unzipResult.zipfile['device'],
                      valid_zipfile_num = self.unzipResult.valid_zipfile['num'],
                      valid_zipfile_comment = self.unzipResult.valid_zipfile['comment'],
                      valid_zipfile_device = self.unzipResult.valid_zipfile['device'],
                      resultzip_num = self.unzipResult.resultzip['num'],
                      resultzip_comment = self.unzipResult.resultzip['comment'],
                      resultzip_device = self.unzipResult.resultzip['device'],
                      valid_resultzip_num = self.unzipResult.valid_resultzip['num'],
                      valid_resultzip_comment = self.unzipResult.valid_resultzip['comment'],
                      valid_resultzip_device = self.unzipResult.valid_resultzip['device']).save()

def _all_clear():
    global inspect_dirs,inspect_files,inspect_png
    inspect_dirs = ['Result']
    inspect_files = ['Result.zip', 'Kat_Performance.csv']
    inspect_png = ('has_jpg', "Result\case\\1") #Result\monkey\img  #Result\case\\1

# Create your views here.
django_lab_source = os.path.join(PROJECT_ROOT,'django_lab_source')
django_lab_dst = os.path.join(PROJECT_ROOT,'django_lab_dst')
tmp = os.path.join(PROJECT_ROOT,'tmp')
detect = None
gmUtil = base.utils.Util()
inspect_dirs,inspect_files='',''
inspect_png = ()
_all_clear()
unzipResult = None

def index(request):
    #清理目录过程放在zip页面的submit按钮点击时，此处不做处理
    # _initiate_unzip_process()
    all_data = Task.objects.all()
    taskunzips = TaskUnzip.objects.all()
    return render(request, 'lab_analysis_tools/index.html', {'all_data':all_data,
                                                             'taskunzips':taskunzips,
                                                             })

def detail(request, url_id):
    global myModel
    # return HttpResponse("You're looking at question %s." % url_id)
    entry = myModel.objects.values().get(id = url_id)
    titles = myModel.objects.values()[0].keys()
    context = {'entry': entry,
               'titles':titles}
    return render(request, 'lab_analysis_tools/detail.html', context)

def title(request,task_id,title):
    title = title.replace("/","\\")
    tmp_problem = Problem.objects.get(name = title)
    all_data = TaskDevice.objects.filter(task = Task.objects.get(task_id = task_id)).filter(problems = tmp_problem)
    return render(request, 'lab_analysis_tools/title.html', {'all_data':all_data})

@cache_page(60 * 15) # 秒数，这里指缓存 15 分钟，不直接写900是为了提高可读性
def all(request,task_id):
    #从数据库中取数据
    task = Task.objects.get(task_id = task_id)
    taskUnzip = TaskUnzip.objects.get(task = task)
    all_data = TaskDevice.objects.filter(task = task)
    fail_set_l = {}

    for device_info in all_data.values().filter(result = 'fail'):
        if device_info['fail_detail'] in fail_set_l:
            fail_set_l[device_info['fail_detail']] += 1
        else:
            fail_set_l[device_info['fail_detail']] = 1
    try:
        fail_set_l.pop('')
    except:
        pass
    for key,value in fail_set_l.items():
            fail_set_l[key] = str(value)

    context = {'taskUnzip':taskUnzip,
               'all_data': all_data,
               'task':task,
               'fail_set_l':fail_set_l,
               'historical': False}
    return render(request, 'lab_analysis_tools/task_all.html', context)

def allUnzip(request):
    # task = Task.objects.get(task_id = os.path.basename(ZipProcess.zippath))
    # logging.info("-------------------task-----------------" + str(task))
    context = {'historical': False,
               }
    return render(request,'lab_analysis_tools/task_all_unzip.html',context)

@cache_page(60 * 15) # 秒数，这里指缓存 15 分钟，不直接写900是为了提高可读性
def his_all(request,task_id):
    #从数据库中取数据
    task = Task.objects.get(task_id = task_id)
    taskUnzip = TaskUnzip.objects.get(task = task)
    all_data = TaskDevice.objects.filter(task = task)
    fail_set_l = {}

    for device_info in all_data.values().filter(result = 'fail'):
        if device_info['fail_detail'] in fail_set_l:
            fail_set_l[device_info['fail_detail']] += 1
        else:
            fail_set_l[device_info['fail_detail']] = 1
    try:
        fail_set_l.pop('')
    except:
        pass
    for key,value in fail_set_l.items():
            fail_set_l[key] = str(value)

    context = {'taskUnzip':taskUnzip,
               'all_data': all_data,
               'task':task,
               'fail_set_l':fail_set_l,
               'historical': True}
    return render(request, 'lab_analysis_tools/task_all.html', context)

def fail_detail(request,task_id,detail): #hasFile_\d*_jpg #hasFile_/d%2A_jpg
    task = Task.objects.get(task_id = task_id)
    detail = detail.replace("/","\\")
    detail = detail.replace("%2A","*")
    if detail == 'Total':
        all_data = TaskDevice.objects.filter(result = 'fail',task = task)
    else:
        all_data = TaskDevice.objects.filter(result = 'fail',fail_detail = detail,task = task)

    return render(request, 'lab_analysis_tools/fail_detail.html', {'all_data':all_data})


class DataOperate(object):
    def __init__(self,myModel):
        self.myModel = myModel

    def get_all_data(self):
        return self.myModel.objects.values()

    def get_titles(self):
        return self.myModel.objects.values()[0].keys()

    def get_data_by_title(self,title,content):
        return self.myModel.objects.values().filter(**{title:content})



def run_analysis_without_zip(request):
    global detect
    try:
        detectunzip = DetectUnzip(ZipProcess.zippath, support_business_xls_zip.xls,support_business_xls_zip.zip)
        detectunzip.analysis()
        detect = detectunzip
        # Run(detectunzip).insertUnzip(os.path.basename(ZipProcess.zippath))
        #todo //不解压之后，task_all.html页面的显示也可以精简
        # time.sleep(1000)
        return HttpResponseRedirect(reverse('allUnzip'))
    except:
        message = r"压缩路径输入错误！！！"
        return render(request, 'lab_analysis_tools/zip.html', {'message': message,})

'''
run_analysis 作为分析主入口，如果有特定业务需求，需要指定不同业务对应的FileScanner
'''

def _run_analysis(task_id):
    global gmUtil
    global django_lab_dst
    global inspect_dirs
    global inspect_files
    global detect
    global inspect_png
    detect = Detect(django_lab_dst,gmUtil)
    detect.hasDirectory(inspect_dirs)
    detect.hasFile(inspect_files)
    detect.contentNumOfDir(inspect_png)


    start = time.time()
    '''
    业务对应的FileScanner
    '''
    fs = detect.getFileScanner(FileScannerXls,support_business_xls_zip.xls)

    # load json data from JSON_ROOT directory
    for jsonConfig in ("logcat_json.txt", "console_json.txt", "error_json.txt", "lualog_json.txt", "lifecycle_json.txt", "accessmanager_json"):
        with open(os.path.join(JSON_ROOT,jsonConfig), 'r') as jsonObject:
            fs.setConfig(JsonConfig(jsonConfig, json.load(jsonObject, encoding='utf-8')))

    detect.analysis()
    logging.info("-----------------analysis-----------------" + str(time.time()-start))
    # 执行插入数据库流程

    start = time.time()
    Run(detect).insert()
    logging.info("-----------------db-----------------" + str(time.time()-start))

    return HttpResponseRedirect(reverse('all',kwargs={'task_id':task_id,}))

def delete_task(request,task_id):
    try:
        Task.objects.get(task_id = task_id).delete()
    except:
        pass
    all_data = Task.objects.all()
    return render(request, 'lab_analysis_tools/index.html', {'all_data':all_data})

def handle_zip_file(filename, mUtil):
    global django_lab_source
    global django_lab_dst
    global tmp
    global unzipResult
    if os.path.exists(filename):
        unzipResult = unzipSource(source_zip_file=filename, \
                                  source_path=django_lab_source, dst_path=django_lab_dst, mUtil=mUtil)
        #todo//目前采用threadpool的方式，并行处理效果不佳
        unzipResult.unzip()
        return True, unzipResult
    return False,unzipResult

class ZipProcess(object):
    zippath = ""

    @classmethod
    def reset(cls):
        cls.zippath = ''

def zipLoadingLabel(request):
    global gmUtil
    message = r"请输入有效的压缩文件绝对路径,例如 C:\54321"

    path_pattern = "path" in request.GET and request.GET['path'] != ""
    xls_pattern = 'xls' in request.GET and request.GET['xls'] != ""
    zip_pattern = 'zip' in request.GET and request.GET['zip'] != ""

    if xls_pattern:
        support_business_xls_zip.xls = request.GET['xls']

    if zip_pattern:
        support_business_xls_zip.zip = request.GET['zip']

    if path_pattern:
        ZipProcess.zippath = request.GET['path']
        return render(request, 'lab_analysis_tools/wait.html')

    return render(request, 'lab_analysis_tools/zip.html', {'message': message,})

def zipProcess(request):
    global gmUtil
    #在zip页面中，开始解压缩处理之前，先执行一遍清理流程，此清理流程和进入index页面执行相同逻辑
    _initiate_unzip_process()
    #todo //开始执行解压处理流程，怎么能够停止？？

    #todo // 调试需要，暂时不做解压处理
    # boolValue, unzipResult = handle_zip_file(ZipProcess.zippath, gmUtil)
    boolValue = True
    # logging.info("---------------unzip--------------------" + str(time.time()-start))
    if boolValue:
        #todo // 调用不解压的分析流程
        # return _run_analysis(unzipResult.task_id)
        return run_analysis_without_zip(request)
    return index(request)

def zip(request):
    support_business_xls_zip.reset()
    ZipProcess.reset()

    return zipLoadingLabel(request)

# def zip(request):
#     support_business_xls_zip.reset()
#     global gmUtil
#     message = r"请输入有效的压缩文件绝对路径,例如 C:\54321.zip"
#
#     path_pattern = "path" in request.GET and request.GET['path'] != ""
#     xls_pattern = 'xls' in request.GET and request.GET['xls'] != ""
#     zip_pattern = 'zip' in request.GET and request.GET['zip'] != ""
#
#     if xls_pattern:
#         support_business_xls_zip.xls = request.GET['xls']
#
#     if zip_pattern:
#         support_business_xls_zip.zip = request.GET['zip']
#
#     if path_pattern:
#         boolValue, unzipResult = handle_zip_file(request.GET['path'], gmUtil)
#         if boolValue:
#             return _run_analysis(unzipResult.task_id)
#     return render(request, 'lab_analysis_tools/zip.html', {'message': message,})


class support_business_xls_zip(object):
    xls = 'com.kunpeng.creeper.default'
    zip = 'com.kunpeng.creeper.default'

    @classmethod
    def reset(cls):
        cls.xls = 'com.kunpeng.creeper.default'
        cls.zip = 'com.kunpeng.creeper.default'


def handle_inspect_files(files):
    global inspect_files
    tmp = files.split(",")
    tmp = [item for item in tmp if item != ""]
    inspect_files.extend(tmp)


def handle_inspect_dirs(dirs):
    global inspect_dirs
    tmp = dirs.split(",")
    tmp = [item for item in tmp if item != ""]
    inspect_dirs.extend(tmp)

def export(request):
    global detect
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    content_Disposition = 'attachment; filename="%s.csv"' % os.path.basename(ZipProcess.zippath)
    response['Content-Disposition'] = content_Disposition
    writer = csv.writer(response)

    # task = Task.objects.get(task_id = task_id)
    # all_data = TaskDevice.objects.filter(task = task)
    #todo// 没有解压过程的导出xls
    all_data = detect.devices
    # titles = poll_extras.getProblemTitle(all_data)
    # for i in ('Detail','Result','Name'):
    #     titles.insert(0,i)
    # writer.writerow(titles)
    writer.writerow(['Name','Result','solution'])

    for taskDevice in all_data:
        tmp_l = []
        tmp_l.append(taskDevice['device'])
        tmp_l.append(taskDevice['result'])
        tmp_l.append(taskDevice['solution'].encode(sys.getfilesystemencoding()))
        # for title in poll_extras.getProblemTitle(all_data):
        #     tmp_l.append(poll_extras.getProblemValue(taskDevice,title))
        writer.writerow(tmp_l)
    return response

def export_zip(request):
    global detect
    try:
        #得到临时压缩文件
        temp = detect.temp
        # 封装临时的zip文件到response中
        wrapper = django.core.files.File(temp)
        response = HttpResponse(wrapper, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=%s.zip' % os.path.basename(ZipProcess.zippath)
        response['Content-Length'] = temp.tell()
        temp.seek(0)
        wrapper.close()
        return response
    except:
        return HttpResponseRedirect(reverse('index'))

def handle_json_file(f):
    try:
        if f.name == 'logcat_json.txt':
            with open(os.path.join(JSON_ROOT,"logcat_json.txt"),'w') as logcat_json:
                for chunk in f.chunks():
                    logcat_json.write(chunk)
            return True
        elif f.name == 'console_json.txt':
            with open(os.path.join(JSON_ROOT,"console_json.txt"),'w') as console_json:
                for chunk in f.chunks():
                    console_json.write(chunk)
            return True
        elif f.name == 'error_json.txt':
            with open(os.path.join(JSON_ROOT,"error_json.txt"),'w') as error_json:
                for chunk in f.chunks():
                    error_json.write(chunk)
            return True
        else:
            return False
    except:
        return False

def _initiate_unzip_process():
    global gmUtil
    global django_lab_source
    global django_lab_dst

    # 清理全局变量
    _all_clear()
    # 首先删除source_path 和 dst_path
    # process = unzipSource(source_zip_file = None,\
    #             source_path = django_lab_source,dst_path = django_lab_dst, mUtil= gmUtil)
    tag = 1
    try:
        while(tag==1):
            if os.path.exists(django_lab_source):
                gmUtil.delete_file_folder(django_lab_source)
            if os.path.exists(django_lab_dst):
                gmUtil.delete_file_folder(django_lab_dst)
            if not os.path.exists(django_lab_source) and \
                not os.path.exists(django_lab_dst):
                tag = 0
        delete_state = "Delete Success"
    except:
        delete_state = "Delete Failed,please delete manually"
    return delete_state

def zip_process(request,parameter):
    task_id, check_point = parameter.split("-")
    #从数据库中取数据：
    task = Task.objects.get(task_id = task_id)
    taskUnzip = TaskUnzip.objects.get(task = task)
    if check_point == 'valid_zipfile':
        device_info = taskUnzip.valid_zipfile_device
    elif check_point == 'resultzip':
        device_info = taskUnzip.resultzip_device
    elif check_point == 'valid_resultzip':
        device_info = taskUnzip.valid_resultzip_device
    device_info_list = device_info.split("\n")
    device_info_list = [item for item in device_info_list if item != '']
    context = {"device_info_list":device_info_list,
               "check_point":'Un-' + check_point,
               "num":len(device_info_list)
               }
    return render(request, 'lab_analysis_tools/zip_process.html', context)

# def trend_su(request):
#     su_timed_out = SuTimedOut()
#     su_timed_out.run()
#     return HttpResponseRedirect(reverse('index'))

# def su_proportionPercentage(request):
#     pp = SuTimedOutProportionPercentage()
#     pp.run()
#     return HttpResponseRedirect(reverse('index'))

# def su_stability(request):
#     ss = SuTimedOutStability()
#     ss.run()
#     return HttpResponseRedirect(reverse('index'))

# def su_searchbydevice(request):
#     if 'device' in request.GET:
#         sd = SuTimedOutSearchByDevice()
#         sd.run(request.GET['device'])
#     return HttpResponseRedirect(reverse('index'))

# def notFoundResultZip(request):
#     #分析TaskUnzip模型数据
#     NotFoundResultZip.objects.all().delete()
#     sqlite3_path = os.path.join(os.path.dirname(PROJECT_ROOT),'db.sqlite3')
#     with sqlite3.connect(sqlite3_path) as con:
#         df_taskunzip = pd.read_sql_query("SELECT * from lab_analysis_tools_taskunzip", con)
#         df_task = pd.read_sql_query("SELECT * from lab_analysis_tools_task", con)
#
#     del df_taskunzip['task_id']
#     del df_taskunzip['id']
#     concatation = pd.concat([df_taskunzip, df_task], axis=1)
#     task_id = concatation.loc[0].task_id
#     task = Task.objects.get(task_id = task_id)
#     all_devices = map(lambda x:x.name, TaskDevice.objects.filter(task=task))
#     index_one_devices = concatation.loc[0].resultzip_device.strip("\n").split("\n")
#     NotFoundResultZip(task=task,
#                       tid=task_id,
#                       all_devices="|".join(all_devices),
#                       problem_devices="|".join(index_one_devices),
#                       repeat_devices='',
#                       unstable_devices='',
#                       newbird_devices="|".join(index_one_devices)).save()
#
#     for i in xrange(1, max(concatation.index)+1):
#         task_id = concatation.loc[i].task_id
#         task = Task.objects.get(task_id=task_id)
#         cur_tmp_devices = concatation.loc[i].resultzip_device.strip("\n").split('\n')
#         pre_all_devices = map(lambda x:x.name, TaskDevice.objects.filter(task=Task.objects.get(task_id=concatation.loc[i-1].task_id)))
#         pre_tmp_devices = concatation.loc[i-1].resultzip_device.strip("\n").split('\n')
#         repeat_devices, unstable_devices, newbird_devices = [], [], []
#         for device_name in cur_tmp_devices:
#             if device_name not in pre_all_devices: # 本次错误设备不在上次所有设备中
#                 newbird_devices.append(device_name)
#             elif device_name in pre_tmp_devices: # 本次错误设备在上次问题设备中
#                 repeat_devices.append(device_name)
#             else:
#                 unstable_devices.append(device_name) # 本次错误设备不在上次问题设备中
#         NotFoundResultZip(task=task,
#                           tid=task_id,
#                           all_devices="|".join(map(lambda x:x.name, TaskDevice.objects.filter(task=task))),
#                           problem_devices="|".join(cur_tmp_devices),
#                           repeat_devices="|".join(repeat_devices),
#                           unstable_devices="|".join(unstable_devices),
#                           newbird_devices="|".join(newbird_devices)).save()
#
#     #展示下新生产的数据
#     not_found_result_zip = NotFoundResultZipV()
#     not_found_result_zip.run()
#     return HttpResponseRedirect(reverse('index'))

@cache_page(60 * 15) # 秒数，这里指缓存 15 分钟，不直接写900是为了提高可读性
def luaunit(request,task_id):
    #lua 单元测试入口
    pass
    global gmUtil
    global django_lab_dst
    detect = Detect(django_lab_dst,gmUtil)
    # load json data from JSON_ROOT directory
    with open(os.path.join(JSON_ROOT,"luaunit_json.txt"),'r') as luaunit_json:
        apis = json.load(luaunit_json)
    with open(os.path.join(JSON_ROOT,"luaunit_sessionid.txt"),'r') as luaunit_sessionid_json:
        sessionId = json.load(luaunit_sessionid_json)
    context_length_apis = len(apis)
    detect.setSessionId(sessionId)
    detect.luaunit("|".join(apis))
    invalid_devices = detect.getLuaunitInvalidDevices()
    #写入数据库
    Run(detect).insert_luaunit()
    #从数据库取出数据并展示
    task = Task.objects.get(task_id = task_id)
    all_data = TaskDevice.objects.filter(task = task)
    all_data = list(all_data)
    context_length_all_data = len(all_data)
    taskUnzip = TaskUnzip.objects.get(task = task)

    #主apis的结构，用来管理主api相关的设备信息
    context_main_apis = []
    main_apis = ["tap","findControl"] #getControlerRect 目前接口不好用，先忽略测试
    for api in main_apis:
        instapi = Api(api)
        instapi_total_num = 0
        for index,taskdevice in enumerate(all_data):
            #基础api被检查发现测试过程中失败，则将此taskdevice从all_data中剔除，供后续的all_data集合处理
            if api in taskdevice.luaunit_fail:
                #此处将失败详情（代表是否找到error.txt文件，pass代表没找到，fail代表找到）拼接到设备名字后面
                instapi.addDevice(taskdevice.name + "**" + taskdevice.fail_detail)
                all_data.pop(index)
                instapi_total_num += 1
            elif api in taskdevice.luaunit_pass:
                instapi_total_num += 1
        instapi.caclulateRate(instapi_total_num)
        context_main_apis.append(instapi)
    context_main_apis = sorted(context_main_apis, key=lambda instapi: instapi.rate)

    #得到除主api之外的apis列表
    context_length_poped_all_data = len(all_data)
    context_other_apis = []
    try:
        for api in main_apis:
            apis.remove(api)
    except:
        pass
    for api in apis:
        instapi = Api(api)
        instapi_total_num = 0
        for taskdevice in all_data:
            if api in taskdevice.luaunit_fail:
                instapi.addDevice(taskdevice.name + "**" + taskdevice.fail_detail)
                instapi_total_num += 1
            elif api in taskdevice.luaunit_pass:
                instapi_total_num += 1
        instapi.caclulateRate(instapi_total_num)
        context_other_apis.append(instapi)
    context_other_apis = sorted(context_other_apis, key=lambda instapi: instapi.rate)

    context = {'taskUnzip':taskUnzip,
               'context_length_apis':context_length_apis,
               'context_length_all_data': context_length_all_data,
               'context_length_poped_all_data':context_length_poped_all_data,
               'task':task,
               'context_main_apis':context_main_apis,
               'context_other_apis':context_other_apis,
               'invalid_devices':invalid_devices,
               }
    return render(request, 'lab_analysis_tools/luaunit.html', context)

class Api(object):
    def __init__(self,name):
        self.name = name
        self.rate = 0
        self.devices = []
        self.color = ""
        self.total = 0

    def addDevice(self,device):
        self.devices.append(device)

    def caclulateRate(self,total):
        self.total = total
        if total == 0:
            self.rate = 0
        else:
            self.rate = round(float(total-len(self.devices))/float(total),2) * 100
        if self.rate<=80:
            self.color = "ff0033"
        elif 80<self.rate<=90:
            self.color = "cccc33"
        elif 90<self.rate<95:
            self.color = "00ff33"
        else:
            self.color = "003300"

def luaunit_devices(request,devices):
    return render(request, 'lab_analysis_tools/luaunit_sub_devices.html', {"devices":devices.split("|")})

def export_luaunit(request,task_id):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    content_Disposition = 'attachment; filename="%s.csv"' % (task_id + "_luaunit")
    response['Content-Disposition'] = content_Disposition
    writer = csv.writer(response)
    task = Task.objects.get(task_id = task_id)
    all_data = TaskDevice.objects.filter(task = task)
    writer.writerow(["Device Name", "Failed APIs", "Passed APIs"])
    for taskDevice in all_data:
        tmp_l = []
        tmp_l.append(taskDevice.name)
        tmp_l.append(taskDevice.luaunit_fail)
        tmp_l.append(taskDevice.luaunit_pass)
        writer.writerow(tmp_l)
    return response











