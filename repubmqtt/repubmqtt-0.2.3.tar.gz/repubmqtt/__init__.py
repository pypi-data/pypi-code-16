#!/usr/bin/python

from __future__ import print_function

import logging
import time
import sys
import json
import re
import string
import requests
import traceback


DBG = 0

# Utility functions


def deepdictvalue(key, ddict, val=None):
	""" extract (or set) a field value from a nested dictionary.
		Raise KeyError if then field does not exits
	"""
	if type(ddict) != type({}):
		raise KeyError("%s - not a dict" % key)
	keys = key.split('.')
	if DBG >= 4: logger.debug('deepdictvalue(%s, %s)', key, ddict.keys())
	if len(keys) == 1:
		if val != None:
			ddict[key] = val
		return ddict[key]
	try:
		return deepdictvalue('.'.join(keys[1:]), ddict[keys[0]], val)
	except KeyError as e:
		if DBG >= 4: logger.debug("deepdictvalue error: key '%s' dict keys: '%s'", keys[0], ddict.keys())
		raise


def extractfromdict(msg, filters):
	""" return a dict populated with values extracted from srcdict
		governed by a filterdict (key = fieldname,  value = re ) """

	def determinekey(name_key):
		""" parse filter name key: [new_name:]name[.name].. """
		fkey = name_key.split(':')
		filter_key = fkey[-1]
		if len(fkey) > 1:
			use_key = fkey[0]
		else:
			use_key = filter_key.split('.')[-1]
		return filter_key, use_key
		
	result_msg = {}
	# 'filter': {'field1': [['>',99],['re','(.*)']], 'field2': 'Test(.*)' }
		
	for filter_name_key in filters:
		filter_key, use_key = determinekey(filter_name_key)
		filter_match = filters[filter_name_key]

		msg_val = deepdictvalue(filter_key, msg)
		if msg_val == None:
			return None;
		if type(filter_match) == type([]):
			filter_match_list = filter_match		# shorthand syntax
		else:
			filter_match_list = [['re', filter_match]]
		match_result = None
		# [['>',99],['re','(.*)']]
		if DBG >= 3: logger.debug("filter_match_list: %s", str(filter_match_list))
		for match_ops in filter_match_list:
			if type(match_ops) != type([]) or len(match_ops) != 2:
				raise SyntaxError ("match ops format "+filter_name_key+" "+str(match_ops))
			if DBG >= 3: logger.debug("filter_match_list %s, msg_val %s", match_ops, msg_val)
			# 'and' result of list ['>',99],['re','(.*)']
			match_type, match_val = match_ops
			if DBG >= 3: logger.debug("match_ops %s %s", match_type, match_val)
			if match_type == 're':
				try:
					r = re.match(str(match_val), str(msg_val))
				except Exception as e:
					raise SyntaxError ("re error %s pattern '%s' value '%s'" % (e, match_val, msg_val))

				if DBG >= 3: logger.debug("extractfromdict: %s: '%s' '%s' -> %s", \
					 filter_name_key, match_ops, str(msg_val),\
					  "not" if r == None else "Match")
				if r:
					try:
						match_result = r.group(1)
					except:
						match_result = r.group(0)
					break
			elif match_type in ['==','<','<=','>','>=', '!=']:
				if str(match_val).replace('.','',1).isdigit():
					msgv = msg_val
					matchv = match_val
				else:
					msgv = "'%s'" % msg_val
					matchv = "'%s'" % match_val
				teval = "%s %s %s" % (msgv, match_type, matchv)
				try:
					r = eval(teval)
				except:
					logger.exception("eval error '%s': " % teval)
					r = False
				if DBG >= 3: logger.debug("eval: %s --> %s", teval, r)
				if r:
					match_result = r
					break   # 
			else:
				raise KeyError("bad match op '%s' filter '%s'" % \
					(match_type, filter_name_key))
 
			if match_result:	# list of 'or' conditions
				break

		if match_result:
			result_msg[use_key] = match_result
		else:
			if DBG >= 3: logger.debug("extractfromdict: fin None")
			raise KeyError(filter_name_key)

	if DBG >= 3: logger.debug("extractfromdict: fin %s", result_msg)
	return result_msg


class RuleSet:
	def __init__(self, ruleset, repub):
		self.name = ruleset['name']
		self.ruleset = ruleset
		self.repub = repub
		self.seen = False
		self.publishers = {}


	def register_publish_protocol(self, name, function):
		self.publishers[name] = function


	def publish(self, pub, new_record):

		def prepdata(template, new_record):
			try:
				ret_data = template % new_record
			except ValueError as e:
				logger.error("rule '%s' publish '%s' error in template '%s' record  '%s': %s", self.name, publish, template, new_record, e)
				ret_data = None
			except KeyError as e:
				ret_data = None
				logger.error( "rule '%s' publish '%s' field '%s' not in record '%s'", self.name, publish, e, new_record)
			return ret_data


		if type(pub) == type([]):
			publish_dict = pub
		else:
			publish_dict = [pub]
		if DBG >= 1: logger.debug("publish: %s", publish_dict)
		for publish in publish_dict:
			if publish.get('once', False) and self.seen:
				continue

			if not 'data' in publish:
				data = "%s"
			else:
				if 'copy_fields' in publish:
					data = self.copydict(publish['data'], publish['copy_fields'], new_record)
					if DBG >= 1: logger.debug("publish: %s %s -> %s", publish['protocol'], data, new_record)
				else:
					data = publish['data']
					if DBG >= 1: logger.debug("publish: %s %s", publish['protocol'], new_record)

			if type(data) == type({}):
				output_data = prepdata(json.dumps(data), new_record)
			else:
				output_data = prepdata(str(data), new_record)

			if output_data:
				publish['_testmode'] = self.repub.testmode
				if publish['protocol'] in self.publishers.keys():
					self.publishers[publish['protocol']](publish, output_data, new_record)
				else:
					logger.error( "publish protocol '%s' not defined", publish['protocol'])
		self.seen = True



	def copydict(self, template, fields, srcdict):
		dstdict = template.copy()
		for dst, src, typ in fields:
			try:
				if typ == 'int':
					deepdictvalue(dst, dstdict, int(float(deepdictvalue(src, srcdict))))
					if DBG >= 3: logger.debug("copydict: int %s", dstdict)
				elif typ == 'float':
					deepdictvalue(dst, dstdict, float(deepdictvalue(src, srcdict)))
					if DBG >= 3: logger.debug("copydict: float %s", dstdict)
				elif typ == '':
					deepdictvalue(dst, dstdict, deepdictvalue(src, srcdict))
					if DBG >= 1: logger.debug("copydict: float %s", dstdict)
				elif typ in self.repub.xlate:
					v=self.repub.xlate[typ][deepdictvalue(src, srcdict)]
					if DBG >= 3: logger.debug("copydict: xlate %s %s %s", v, deepdictvalue(src, srcdict), self.repub.xlate[typ])
					deepdictvalue(dst, dstdict, v)
					if DBG >= 3: logger.debug("copydict: xlate %s", dstdict)
			except Exception as e:
				logger.error( "copy_fields error '%s' dst '%s' src '%s' type '%s' in '%s'", \
					e, dst, src, typ, str(srcdict))
		return dstdict


class Republish:
	defaultlog = {
		'name': 'defaultlog',
		'rules': [['', '', 'publish']],
		'publish': [{'protocol': 'log' }]
	}
	def __init__(self, rules, xlate, log_name='root'):
		global logger
		logger = logging.getLogger(log_name+"."+__name__)

		self.rulesets = {}
		self.xlate = xlate
		self.testmode = False

		if len(rules) == 0:
			rules = [Republish.defaultlog]
		for r in rules:
			rs = RuleSet(r, self)
			if rs.name in self.rulesets:
				logger.error( "RuleSet %s already defined", rs.name)
				sys.exit(1)
			self.rulesets[rs.name] = rs
			if DBG >= 1: logger.debug("added rulesets %s", rs.name)

		self.register_publish_protocol('log', self.publish_log)


	def setdebuglevel(self, dbg):
		global DBG
		DBG = dbg
		if DBG: print("DBG set to", DBG)


	def register_publish_protocol(self, name, function):
		for r in self.rulesets:
			self.rulesets[r].register_publish_protocol(name, function)


	def settestmode(self, mode):
		self.testmode = mode


	def process_message(self, jrecord):

		def filter_record(jrecord, filter_code):

			try:
				filter_result = extractfromdict(jrecord, filter_code)
			except KeyError as e:
				if DBG >= 1: logger.debug("filter ruleset '%s' '%s': blocked! field '%s' not present", \
					rule_name, filter_name, e)
				return None
			except ValueError as e:
				if DBG >= 1: logger.debug("filter ruleset '%s' '%s': blocked! field '%s' no value", \
					rule_name, filter_name, e)
				return None
			except SyntaxError as e:
				logger.error( "filter ruleset '%s' '%s': blocked! syntax eror: %s", \
					rule_name, filter_name, e)
				return None
			if filter_result != None:
				if DBG >= 1: logger.debug("filter ruleset '%s' '%s': passed!", \
					 rule_name, filter_name)
			return filter_result


		def select_record(jrecord, selector_code):
			try:
				select_result = extractfromdict(jrecord, selector_code)
			except KeyError as e:
				logger.error("selector ruleset '%s', '%s' field %s not in record '%s'", rule_name, selector_code, e, str(jrecord))
				return None
			except ValueError as e:
				logger.error("selector ruleset '%s', '%s' field %s  value mismatch  '%s'", rule_name, selector_code, e, str(jrecord))
				return None
			except SyntaxError as e:
				logger.error( "selector ruleset '%s' '%s': syntax eror: %s", \
					rule_name, filter_name, e)
				return None
			select_result['ts'] = jrecord['ts']
			return select_result


		if DBG >= 1: logger.debug("input %s", jrecord)
		if not 'ts' in jrecord:
			time_stamp = time.time()
			ts=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time_stamp))
			jrecord['ts'] = ts
	
		select_result = None
		for rule in self.rulesets:
			ruleset = self.rulesets[rule].ruleset
			rule_name = ruleset['name']
			for filter_name, selector_name, publish_name in ruleset['rules']:
				# no filter means pass
				if not filter_name:
					filter_result = jrecord
				else:
					filter_code = ruleset[filter_name]
					error_locus = 'filter '+rule_name

					filter_result = filter_record(jrecord, filter_code)
				if filter_result == None:
					continue

				# filter passed, now select
				error_locus =  'selector '+rule_name
				if not selector_name:
					select_result = jrecord
				else:
					selector_code = ruleset[selector_name]
					select_result = select_record(jrecord, selector_code)

				if select_result == None:
					continue

				if DBG >= 1: logger.debug("selector ruleset '%s' '%s': selected: %s", \
					 rule_name, filter_name, str(select_result))
				if publish_name:
					publish_list = ruleset[publish_name]
					self.rulesets[rule].publish(publish_list, select_result)


	def publish_log(self, publish, output_data, data):
		fname = publish.get('logfile','')
		if publish['_testmode']:
			logger.info("testmode: publish_log (%s) %s", fname, str(output_data))
			return
		if fname:
			f = open(fname,"a+")
		else:
			f = sys.stdout
		print(output_data,file=f)
		if fname:
			f.close()


