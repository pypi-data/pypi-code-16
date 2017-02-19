# -*- coding: UTF-8 -*-
#
# @author huangyue<huangyue@haodou.com>
# @since 17/2/17
#

import os
dirname, filename = os.path.split(os.path.abspath(__file__))



def fav_import_main():
    config = "%s/mongo_connector_doc_managers/config_fav.json" %(dirname)
    command = "python mongo-connector -c %s" %(config)
    res = os.system(command=command)
    print res

def favdir_import_main():
    try:
        config = "%s/mongo_connector_doc_managers/config_favdir.json" % (dirname)
        # command = "nohup mongo-connector -c %s &" % (config)
        command = " mongo-connector -c %s " % (config)
        # res = os.system(command=command)
        # print res
        output = os.popen(command)
        print output.read()
    except Exception as e:
        print e





favdir_import_main()
