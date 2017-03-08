# -*- coding: utf-8 -*-

NAME = 'batchcompute-cli'

COMMAND = 'batchcompute|bcs'
CMD = 'bcs'

LOCALE_SUPPORTED = ['en', 'zh', 'zh_CN']

VERSION = '1.3.10a1'

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
    "ecs.t1.small":{"cpu":1,"memory":1,"name":"ecs.t1.small"},
    "ecs.s3.large":{"name":"ecs.s3.large","cpu":4,"memory":8},
    "ecs.m1.medium":{"name":"ecs.m1.medium","cpu":4,"memory":16},
    "ecs.m2.medium":{"name":"ecs.m2.medium","cpu":4,"memory":32},
    "ecs.c1.large":{"name":"ecs.c1.large","cpu":8,"memory":16},
    "ecs.m1.xlarge":{"name":"ecs.m1.xlarge","cpu":8,"memory":32},
    "ecs.m2.xlarge":{"cpu":8,"memory":64,"name":"ecs.m2.xlarge"},
    "ecs.c2.medium":{"name":"ecs.c2.medium","cpu":16,"memory":16},
    "ecs.c2.large":{"name":"ecs.c2.large","cpu":16,"memory":32},
    "ecs.c2.xlarge":{"name":"ecs.c2.xlarge","cpu":16,"memory":64},
    "bcs.a2.large":{"cpu":4,"memory":8,"name":"bcs.a2.large"},
    "bcs.a2.xlarge":{"cpu":8,"memory":16,"name":"bcs.a2.xlarge"},
    "bcs.a2.3xlarge":{"cpu":16,"memory":32,"name":"bcs.a2.3xlarge"},
    "bcs.b2.3xlarge":{"cpu":16,"memory":32,"name":"bcs.b2.3xlarge"},
    "bcs.b4.xlarge":{"cpu":8,"memory":32,"name":"bcs.b4.xlarge"},
    "bcs.b4.3xlarge":{"cpu":16,"memory":64,"name":"bcs.b4.3xlarge"},
    "bcs.b4.5xlarge":{"cpu":24,"memory":96,"name":"bcs.b4.5xlarge"},
    "bcs.a2.4xlarge":{"cpu":20,"memory":40,"name":"bcs.a2.4xlarge","disk":400},
    "bcs.b4.4xlarge":{"cpu":20,"memory":80,"name":"bcs.b4.4xlarge","disk":1000},
    "ecs.n1.xlarge":{"name":"ecs.n1.xlarge","cpu":8,"memory":16},
    "ecs.n1.3xlarge":{"name":"ecs.n1.3xlarge","cpu":16,"memory":32},
    "ecs.n4.2xlarge":{"name":"ecs.n4.2xlarge","cpu":8,"memory":16},
    "ecs.n4.4xlarge":{"name":"ecs.n4.4xlarge","cpu":16,"memory":32},
    "ecs.sn1.large":{"name":"ecs.sn1.large","cpu":4,"memory":8},
    "ecs.sn1.xlarge":{"name":"ecs.sn1.xlarge","cpu":8,"memory":16},
    "ecs.sn2.large":{"name":"ecs.sn2.large","cpu":4,"memory":16},
    "ecs.sn2.xlarge":{"name":"ecs.sn2.xlarge","cpu":8,"memory":32},
    "ecs.se1.large":{"cpu":2,"memory":16,"name":"ecs.se1.large"},
    "ecs.xn4.small":{"name":"ecs.xn4.small","cpu":1,"memory":1},
    "ecs.n4.large":{"name":"ecs.n4.large","cpu":2,"memory":4},
    "ecs.n4.xlarge":{"name":"ecs.n4.xlarge","cpu":4,"memory":8},
    "ecs.mn4.small":{"name":"ecs.mn4.small","cpu":1,"memory":4},
    "ecs.mn4.large":{"name":"ecs.mn4.large","cpu":2,"memory":8},
    "ecs.mn4.xlarge":{"name":"ecs.mn4.xlarge","cpu":4,"memory":16},
    "ecs.c4.xlarge":{"cpu":4,"memory":8,"name":"ecs.c4.xlarge"},
    "ecs.cm4.xlarge":{"cpu":4,"memory":16,"name":"ecs.cm4.xlarge"},
    "ecs.ce4.large":{"cpu":4,"memory":32,"name":"ecs.ce4.large"},
    "ecs.i1.large":{"cpu":4,"memory":16,"name":"ecs.i1.large"},
    "ecs.s1.small":{"cpu":1,"memory":2,"name":"ecs.s1.small"},
    "ecs.s1.medium":{"cpu":1,"memory":4,"name":"ecs.s1.medium"},
    "ecs.s2.small":{"cpu":2,"memory":2,"name":"ecs.s2.small"},
    "ecs.s2.large":{"name":"ecs.s2.large","cpu":2,"memory":4},
    "ecs.s2.xlarge":{"name":"ecs.s2.xlarge","cpu":2,"memory":8},
    "ecs.s3.medium":{"name":"ecs.s3.medium","cpu":4,"memory":4},
    "ecs.n1.small":{"name":"ecs.n1.small","cpu":1,"memory":2},
    "ecs.n1.medium":{"name":"ecs.n1.medium","cpu":2,"memory":4},
    "ecs.n1.large":{"name":"ecs.n1.large","cpu":4,"memory":8},
    "ecs.n2.small":{"name":"ecs.n2.small","cpu":1,"memory":4},
    "ecs.n2.medium":{"name":"ecs.n2.medium","cpu":2,"memory":8},
    "ecs.n2.large":{"name":"ecs.n2.large","cpu":4,"memory":16},
    "ecs.e3.small":{"name":"ecs.e3.small","cpu":1,"memory":8},
    "ecs.e3.medium":{"name":"ecs.e3.medium","cpu":2,"memory":16},
    "ecs.n4.small":{"name":"ecs.n4.small","cpu":1,"memory":2},
    "ecs.n4.8xlarge":{"name":"ecs.n4.8xlarge","cpu":32,"memory":64},
    "ecs.mn4.2xlarge":{"name":"ecs.mn4.2xlarge","cpu":8,"memory":32},
    "ecs.mn4.4xlarge":{"name":"ecs.mn4.4xlarge","cpu":16,"memory":64},
    "ecs.mn4.8xlarge":{"name":"ecs.mn4.8xlarge","cpu":32,"memory":128},
    "ecs.e4.small":{"name":"ecs.e4.small","cpu":1,"memory":8},
    "ecs.e4.large":{"name":"ecs.e4.large","cpu":2,"memory":16},
    "ecs.e4.xlarge":{"name":"ecs.e4.xlarge","cpu":4,"memory":32},
    "ecs.e4.2xlarge":{"name":"ecs.e4.2xlarge","cpu":8,"memory":64},
    "ecs.e4.4xlarge":{"name":"ecs.e4.4xlarge","cpu":16,"memory":128},
    "ecs.n1.tiny":{"name":"ecs.n1.tiny","cpu":1,"memory":1},
    "ecs.n1.7xlarge":{"name":"ecs.n1.7xlarge","cpu":32,"memory":64},
    "ecs.n2.xlarge":{"name":"ecs.n2.xlarge","cpu":8,"memory":32},
    "ecs.n2.3xlarge":{"name":"ecs.n2.3xlarge","cpu":16,"memory":64},
    "ecs.n2.7xlarge":{"name":"ecs.n2.7xlarge","cpu":32,"memory":128},
    "ecs.e3.large":{"name":"ecs.e3.large","cpu":4,"memory":32},
    "ecs.e3.xlarge":{"name":"ecs.e3.xlarge","cpu":8,"memory":64},
    "ecs.e3.3xlarge":{"name":"ecs.e3.3xlarge","cpu":16,"memory":128},
    "ecs.sn1.medium":{"name":"ecs.sn1.medium","cpu":2,"memory":4},
    "ecs.sn1.3xlarge":{"name":"ecs.sn1.3xlarge","cpu":16,"memory":32},
    "ecs.sn1.7xlarge":{"name":"ecs.sn1.7xlarge","cpu":32,"memory":64},
    "ecs.sn2.medium":{"name":"ecs.sn2.medium","cpu":2,"memory":8},
    "ecs.sn2.3xlarge":{"name":"ecs.sn2.3xlarge","cpu":16,"memory":64},
    "ecs.sn2.7xlarge":{"name":"ecs.sn2.7xlarge","cpu":32,"memory":128},
    "ecs.sn2.9xlarge":{"name":"ecs.sn2.9xlarge","cpu":40,"memory":224},
    "ecs.s2.2xlarge":{"name":"ecs.s2.2xlarge","cpu":2,"memory":16},
    "ecs.c1.small":{"name":"ecs.c1.small","cpu":8,"memory":8}
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



