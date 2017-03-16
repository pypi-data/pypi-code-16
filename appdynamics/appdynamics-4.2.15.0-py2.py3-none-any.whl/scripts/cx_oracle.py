# Copyright (c) AppDynamics, Inc., and its affiliates
# 2016
# All Rights Reserved

"""The public interface to an instrumented version of cx_Oracle.

Import this module and use in exactly the same way as you would the normal
cx_Oracle.  The behavior is exactly the same.

"""

from cx_Oracle import *
from appdynamics.agent.interceptor.sql.cx_oracle import Connection, Cursor

connect = Connection
