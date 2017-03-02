# -*- coding: utf-8 -*-
# @Author: ZwEin
# @Date:   2016-06-30 13:23:24
# @Last Modified by:   ZwEin
# @Last Modified time: 2016-11-08 14:47:49

import os
import json

def load_groundtruth(path=os.path.join(os.path.dirname(__file__), "groundtruth.json")):
    input_fh = open(path, 'rb')
    lines = input_fh.readlines()
    json_obj = json.loads(''.join(lines))
    jsonlines = json_obj['jsonlines']
    return jsonlines


if __name__ == "__main__":
    print json.dumps(load_groundtruth(), indent=4)