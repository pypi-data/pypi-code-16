# -*- coding: utf-8 -*-

NAME = 'batchcompute-cli'

COMMAND = 'batchcompute|bcs'
CMD = 'bcs'

LOCALE_SUPPORTED = ['en', 'zh', 'zh_CN']

VERSION = '1.3.7'

EVENTS = {
    'CLUSTER': [
        "OnClusterDeleted",
        "OnInstanceCreated",
        "OnInstanceActive"
    ],
    'JOB': [
        "OnJobWaiting",
        "OnJobRunning",
        "OnJobStopped",
        "OnJobFinished",
        "OnJobFailed",
        "OnTaskWaiting",
        "OnTaskRunning",
        "OnTaskStopped",
        "OnTaskFinished",
        "OnTaskFailed",
        "OnInstanceWaiting",
        "OnInstanceRunning",
        "OnInstanceStopped",
        "OnInstanceFinished",
        "OnInstanceFailed",
        "OnPriorityChange"
    ]
}

IT_MAP = {
    'ecs.t1.small': {'cpu': 1, 'memory': 1, 'name': 'ecs.t1.small'},
    'ecs.s3.large': {'cpu': 4, 'memory': 8, 'name': 'ecs.s3.large'},
    'ecs.m1.medium': {'cpu': 4, 'memory': 16, 'name': 'ecs.m1.medium'},
    'ecs.m2.medium': {'cpu': 4, 'memory': 32, 'name': 'ecs.m2.medium'},
    'ecs.c1.large':{'cpu': 8, 'memory': 16, 'name': 'ecs.c1.large'},
    'ecs.m1.xlarge': {'cpu': 8, 'memory': 32, 'name': 'ecs.m1.xlarge'},
    'ecs.m2.xlarge':{'cpu': 8, 'memory': 64, 'name': 'ecs.m2.xlarge'},
    'ecs.c2.medium':{'cpu': 16, 'memory': 16, 'name': 'ecs.c2.medium'},
    'ecs.c2.large':{'cpu': 16, 'memory': 32, 'name': 'ecs.c2.large'},
    'ecs.c2.xlarge':{'cpu': 16, 'memory': 64, 'name': 'ecs.c2.xlarge'},
    'bcs.a2.large':    {'cpu': 4, 'memory': 8, 'name': 'bcs.a2.large'},
    'bcs.a2.xlarge': {'cpu': 8, 'memory': 16, 'name': 'bcs.a2.xlarge'},
    'bcs.a2.3xlarge':  {'cpu': 16, 'memory': 32, 'name': 'bcs.a2.3xlarge'},
    'bcs.b2.3xlarge': {'cpu': 16, 'memory': 32, 'name': 'bcs.b2.3xlarge'},
    'bcs.b4.xlarge':{'cpu': 8, 'memory': 32, 'name':'bcs.b4.xlarge'},
    'bcs.b4.3xlarge': {'cpu': 16, 'memory': 64, 'name': 'bcs.b4.3xlarge'},
    'bcs.b4.5xlarge': {'cpu': 24, 'memory': 96, 'name': 'bcs.b4.5xlarge'},

    'bcs.a2.4xlarge': {'cpu': 20, 'memory': 40, 'name': 'bcs.a2.4xlarge', 'disk': 400},
    'bcs.b4.4xlarge': {'cpu': 20, 'memory': 80, 'name': 'bcs.b4.4xlarge', 'disk': 1000},

    'ecs.n1.xlarge': {"cpu": 8, "memory": 16, "name": "ecs.n1.xlarge" },
    'ecs.n1.3xlarge': {"cpu": 16, "memory": 32, "name": "ecs.n1.3xlarge" },
    'ecs.n4.2xlarge': {"cpu": 8, "memory": 16, "name": "ecs.n4.2xlarge" },
    'ecs.n4.4xlarge': {"cpu": 16, "memory": 32, "name": "ecs.n4.4xlarge" }
}
#
# IT = {
#     'cn-qingdao': {
#         'data': [
#             {'cpu': 4, 'memory': 8, 'name': 'ecs.s3.large'},
#             #{'cpu': 4, 'memory': 16, 'name': 'ecs.m1.medium'},
#             #{'cpu': 4, 'memory': 32, 'name': 'ecs.m2.medium'},
#             {'cpu': 8, 'memory': 16, 'name': 'ecs.c1.large'},
#             #{'cpu': 8, 'memory': 32, 'name': 'ecs.m1.xlarge'},
#             #{'cpu': 8, 'memory': 64, 'name': 'ecs.m2.xlarge'},
#             #{'cpu': 16, 'memory': 16, 'name': 'ecs.c2.medium'},
#             {'cpu': 16, 'memory': 32, 'name': 'ecs.c2.large'},
#             #{'cpu': 16, 'memory': 64, 'name': 'ecs.c2.xlarge'}
#         ],
#         'default': 'ecs.s3.large'
#     },
#     'cn-shenzhen': {
#         'data': [
#             {'cpu': 4, 'memory': 8, 'name':'bcs.a2.large'},
#             {'cpu': 8, 'memory': 16, 'name': 'bcs.a2.xlarge'},
#             {'cpu': 16, 'memory': 32, 'name':'bcs.a2.3xlarge'},
#             # {'cpu': 16, 'memory': 32, 'name': 'bcs.b2.3xlarge'},
#             # {'cpu': 8, 'memory': 32, 'name':'bcs.b4.xlarge'},
#             # {'cpu': 16, 'memory': 64, 'name': 'bcs.b4.3xlarge'},
#             # {'cpu': 24, 'memory': 96, 'name': 'bcs.b4.5xlarge'},
#         ],
#         'default': 'bcs.a2.large'
#     },
#     'cn-beijing': {
#         'data': [
#             {'cpu': 4, 'memory': 8, 'name': 'bcs.a2.large'},
#             {'cpu': 8, 'memory': 16, 'name': 'bcs.a2.xlarge'},
#             {'cpu': 16, 'memory': 32, 'name': 'bcs.a2.3xlarge'}
#         ],
#         'default': 'bcs.a2.large'
#     },
#     'cn-hangzhou': {
#         'data': [
#             {'cpu': 4, 'memory': 8, 'name': 'bcs.a2.large'},
#             {'cpu': 8, 'memory': 16, 'name': 'bcs.a2.xlarge'},
#             {'cpu': 16, 'memory': 32, 'name': 'bcs.a2.3xlarge'}
#         ],
#         'default': 'bcs.a2.large'
#     }
# }
#
#
#
# IMG = {
#     'cn-qingdao': {
#         'data': [],
#         'default': 'm-28ga7wbnb'
#     },
#     'cn-shenzhen': {
#         'data': [],
#         'default': 'm-94kl8am5i'
#     },
#     'cn-beijing': {
#         'data': [],
#         'default': 'm-251on8h21'
#     },
#     'cn-hangzhou': {
#         'data': [],
#         'default': 'm-23emxj6rq'
#     }
# }


from .util import config


configObj = config.getConfigs(config.COMMON)
region = configObj.get('region')
if region:
    REGION = region

IS_GOD = configObj.get('god') or False



# try:
#     IT_DATA = IT[REGION]['data']
#     INS_TYPE = configObj.get('defaulttype') or IT[REGION]['default']
#     IMG_ID = configObj.get('defaultimage') or IMG[REGION]['default']
#
# except Exception as e:
#     IT_DATA = IT['cn-qingdao']['data']
#     INS_TYPE= configObj.get('defaulttype') or 'ecs.s3.large'
#     IMG_ID = configObj.get('defaultimage') or IMG['cn-qingdao']['default']



import sys


# Python 2 or Python 3 is in use.
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
WIN = sys.platform == 'win32'

# Definition of descriptor types.
if PY2:
    STRING = (str, unicode)
    NUMBER = (int, long)

if PY3:
    STRING = (str, bytes)
    NUMBER = int


# fix chinese view
def get_local():
    return codecs.lookup(locale.getpreferredencoding()).name
if PY2:
    import locale
    import codecs
    try:
        reload(sys)
        loc = get_local()
        sys.setdefaultencoding(loc) # utf-8
    except:
        pass



