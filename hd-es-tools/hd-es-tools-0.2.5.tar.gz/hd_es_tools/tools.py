# -*- coding: UTF-8 -*-
#
# @author huangyue<huangyue@haodou.com>
# @since 17/2/17
#

import os

dirname, filename = os.path.split(os.path.abspath(__file__))

def fav_import_main():
    try:
        config = "%s/mongo_connector_doc_managers/config_fav.json" % (dirname)
        command = "nohup python mongo-connector -c %s 1>/dev/null 2>&1 &" % (config)
        print command
        # res = os.system(command=command)
        # print res
    except Exception as e:
        print e


def favdir_import_main():
    try:
        config = "%s/mongo_connector_doc_managers/config_favdir.json" % (dirname)
        command = "nohup mongo-connector -c %s 1>/dev/null 2>&1 &" % (config)
        # command = " mongo-connector -c %s " % (config)
        print command

        # res = os.system(command=command)
        # print res
        # # output = os.popen(command)
        # # print output.read()
        #
        # sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
        # sys.exit(fav_import_main())
    except Exception as e:
        print e
