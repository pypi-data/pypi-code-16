# -*- coding: utf-8 -*-
import os, sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print BASE_DIR
sys.path.insert(1,BASE_DIR)

import easyRedisCache
easyRedisCache.test()
