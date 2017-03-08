#!/usr/bin/env python -tt

import hashlib
import hmac
import httplib
import urllib
import re
import sys
import time
import json
import os
import email



class Isight():
	def __init__(self):
		self.public_key = ''
		self.private_key = ''
		self.accept_version = '2.3'
		self.accept_header = 'application/json'
		self.time_stamp = email.Utils.formatdate(localtime=True)
		self.custom_timers = {}

	def querySIGHT(self, query_item):
		"""
		query preperation/extraction - output: set(query1, query2, .....)
		"""
		self.domain_regex = re.compile(r'^(?=.{4,255}$)([a-zA-Z0-9][a-zA-Z0-9-]{,61}[a-zA-Z0-9]\.)+[a-zA-Z0-9]{2,5}$')
		self.ip_regex = re.compile(r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")
		self.md5_regex = re.compile(r"\b([a-f\d]{32}|[A-F\d]{32})\b")
		self.sha1_regex = re.compile(r"\b([a-f\d]{40}|[A-F\d]{40})\b")
		self.file_regex = re.compile(r"\w+\.\w{3,4}")
		self.query_set = set()

		if type(query_item) is not list:
			query_item = query_item.replace(' ', '')

			if ( re.match(self.domain_regex ,query_item) or re.match(self.ip_regex ,query_item) or 
				 re.match(self.md5_regex, query_item)  or re.match(self.sha1_regex, query_item) or 
				 re.match(self.file_regex, query_item)):
				self.query_set.add(query_item)
			
			else:
				pass
		if type(query_item) is list:
			for item in query_item:
				if (re.match(self.domain_regex,item) or re.match(self.ip_regex,item) or 
				   re.match(self.md5_regex,item) or re.match(self.sha1_regex, item) or 
				   re.match(self.file_regex, item)):
					self.query_set.add(item)
		
		self.submission_dict = dict()
		if self.query_set:
			for elem in self.query_set:
				if re.match(self.domain_regex, elem):
					enc_q = "/search/basic?domain={domain_name}".format(domain_name=elem)
				if re.match(self.ip_regex, elem):
					enc_q = "/search/basic?ip={ip}".format(ip=elem)
				if re.match(self.md5_regex, elem):
					enc_q = "/search/basic?md5={md5}".format(md5=elem)
				if re.match(self.sha1_regex, elem):
					enc_q = "/search/basic?sha1={sha1}".format(sha1=elem)
				if re.match(self.file_regex, elem):
					enc_q = "/search/text?text={file_name}".format(file_name=elem)
				domain_data = enc_q + self.accept_version + self.accept_header + self.time_stamp
				hashed = hmac.new(self.private_key, domain_data, hashlib.sha256)
				headers = {
				'Accept' : self.accept_header,
				'Accept-Version' : self.accept_version,
				'X-Auth' : self.public_key,
				'X-Auth-Hash' : hashed.hexdigest(),
				'Date'  :  self.time_stamp,
				}
				self.submission_dict[elem] = [enc_q, headers]
			self.results = {k: [] for k in self.submission_dict.keys()}
			conn = httplib.HTTPSConnection('api.isightpartners.com')
			for k, v in self.submission_dict.items():
				conn.request('GET', self.submission_dict[k][0], '', self.submission_dict[k][1])
				try:
					resp = conn.getresponse()
					data = resp.read()
					data = json.loads(data)
					status = resp.status
					if status != 200:
						del self.submission_dict[k]
					else: 
						for num in range(0,len(data['message'])):
							self.results[k].append(data['message'][num]['webLink'])
							break
				except ValueError:
					pass

			{self.results[k].append(len(v)) for k, v in self.results.items()}
			self.results = dict((k, v) for k, v in self.results.items() if len(v) > 1)
			if self.results:
				return self.results
				

