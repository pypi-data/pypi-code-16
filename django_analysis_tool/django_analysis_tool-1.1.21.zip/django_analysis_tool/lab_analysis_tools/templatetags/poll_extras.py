__author__ = 'creeper'
from django import template
from lab_analysis_tools.models import Task,TaskDevice,Problem, TaskUnzip

register = template.Library()

@register.filter(name='cut')
def cut(value, arg):
    return value.replace(arg, '')

@register.filter
def lower(value):
    return value.lower()

@register.filter(name='createDevicesMatrix')
def createDevicesMatrix(all_data):
    return all_data
    # titles = []
    # for taskDevice in all_data:
    #     name = taskDevice.name
    #     problems = taskDevice.problem.all()
    #     task = taskDevice.task
    #     result = taskDevice.result
    #     fail_detail = taskDevice.fail_detail

@register.filter
def getProblemValue(taskDevice,problem_name):
    try:
        taskDevice.problems.get(name=problem_name)
        return 'fail'
    except:
        return ''

@register.filter
def getProblemTitle(all_data):
    titles = []
    for taskDevice in all_data:
        problems = taskDevice.problems.all()
        titles.extend([problem.name for problem in problems])
    return list(set(titles))

@register.filter
def getProblemNum(all_data,problem_name):
    tmp_problem= Problem.objects.get(name = problem_name)
    return len(all_data.filter(problems = tmp_problem))
    # tmp_task = Task.objects.get(task_id = '2852')
    # return len(tmp_problem.taskdevice_set.filter(task = tmp_task))

@register.filter(name='getResult')
def getSubDevicesByResult(all_data,tag):
    return all_data.filter(result = tag)

@register.filter(name='zipfile')
def getKeyFromzipfile(taskUnzip,key):
    if key == 'num':
        return taskUnzip.zipfile_num
    elif key == 'comment':
        return taskUnzip.zipfile_comment
    elif key == 'device':
        return taskUnzip.zipfile_device

@register.filter(name='valid_zipfile')
def getKeyFromvalid_zipfile(taskUnzip,key):
    if key == 'num':
        return taskUnzip.valid_zipfile_num
    elif key == 'comment':
        return taskUnzip.valid_zipfile_comment
    elif key == 'device':
        return taskUnzip.valid_zipfile_device

@register.filter(name='resultzip')
def getKeyFromresultzip(taskUnzip,key):
    if key == 'num':
        return taskUnzip.resultzip_num
    elif key == 'comment':
        return taskUnzip.resultzip_comment
    elif key == 'device':
        return taskUnzip.resultzip_device

@register.filter(name='valid_resultzip')
def getKeyFromvalid_resultzip(taskUnzip,key):
    if key == 'num':
        return taskUnzip.valid_resultzip_num
    elif key == 'comment':
        return taskUnzip.valid_resultzip_comment
    elif key == 'device':
        return taskUnzip.valid_resultzip_device

@register.filter(name="unvalid_resultzip_num")
def getKyeFromunvalid_resultzip_num(taskUnzip):
    return int(taskUnzip.zipfile_num) - int(taskUnzip.valid_resultzip_num)

# index_getId
@register.filter
def index_getId(task):
    return task.task_id

# index_getTotalNum
@register.filter
def index_getTotalNum(task):
    return len(TaskDevice.objects.filter(task = task))

# index_getPassNum
@register.filter
def index_getPassNum(task):
    return len(TaskDevice.objects.filter(task = task,result = 'pass'))


# index_getFailNum
@register.filter
def index_getFailNum(task):
    return len(TaskDevice.objects.filter(task = task,result = 'fail'))

@register.filter
def addString(str1,str2):
    return str1 + str2

@register.filter
def toString(miters):
    return "|".join(miters)

@register.filter
def luaunit_sub_devices_device(content, separator):
    return content.split(separator)[0]

@register.filter
def luaunit_sub_devices_error_txt(content, separator):
    return content.split(separator)[-1]

@register.filter
def getTaskUnzip_valid_resultzip_num(task):
    taskUnzip = TaskUnzip.objects.get(task = task)
    return taskUnzip.valid_resultzip_num

@register.filter
def getTaskUnzip_unvalid_resultzip_num(task):
    taskUnzip = TaskUnzip.objects.get(task = task)
    total = int(taskUnzip.zipfile_num)
    valid = int(taskUnzip.valid_resultzip_num)
    return total-valid

@register.filter
def getTaskUnzip_all_resultzip_num(task):
    taskUnzip = TaskUnzip.objects.get(task = task)
    return taskUnzip.zipfile_num