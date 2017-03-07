#!/usr/bin/env python
# -*- coding: utf-8 -*-

from crate import client
import json
import sys,os

def read_data_CBG(crate_host):
	connection = client.connect(crate_host, error_trace=True)
	cursor =connection.cursor()
	sql = "select * from riot where node_id ='CBGDemo' limit 10"
	cursor.execute(sql)
	return cursor.fetchall()
