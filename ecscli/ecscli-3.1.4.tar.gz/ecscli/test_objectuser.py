from ecscli import runCmd
from ecscli import main_parser
import common
import sys
import inspect

from test_common import *

def objectuser_list_uid(silent=False):
    #case5(True)
    sys.argv = ["", "objectuser", "list", "-uid", "joeouser", "-namespace", "conerj"]
    result = runCmd()
    printit(result, silent)

def case5(silent=False):
    objectuserList = []
    sys.argv = ["", "objectuser", "list", "-hostname"]
    result = runCmd()
    #printit(result)
    blobuser = result['blobuser']
    for b in blobuser:
        userid = b['userid']
        objectuserList.append(userid)
        print(userid)
    return objectuserList

def createtags(silent=False):
    sys.argv = ["", "objectuser", "set-usertag", "-uid", "wsuser_850_20015", "-ts", "tag1^val1", "tag2^val2"] 
    result = runCmd()
    printit(result, silent)

