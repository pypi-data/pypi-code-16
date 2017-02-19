# -*- coding: utf-8 -*-
'''
@author: saaj
'''


try:
  import pymysql
except ImportError:
  pass
else:
  pymysql.install_as_MySQLdb()

import MySQLdb as mysql

