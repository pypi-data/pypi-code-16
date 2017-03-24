#!/usr/bin/env PYTHONIOENCODING="utf-8" python
# -*- coding: utf-8 -*-
import locale
import os
import re
import os.path
import dill as pickle  # BEST! no more Can't pickle <function
import json
import codecs  # codecs.open(file, "r", "utf-8")

try:  # pathetic python3 !
	from urllib2 import urlopen
	from urllib import urlretrieve
except ImportError:
	from urllib.request import urlopen, urlretrieve  # library HELL

from extensions import *  # for functions
import extensions
from os.path import expanduser

api = "http://netbase.pannous.com/json/all/"
api_list = "http://netbase.pannous.com/json/short/"
api_all = "http://netbase.pannous.com/json/query/all/"
my_locale=	locale.getdefaultlocale()
# locale.windows_locale[ windll.GetUserDefaultUILanguage() ]
# NSLocale.current.languageCode #@swift
if "de" in my_locale:
	api = "http://de.netbase.pannous.com/json/all/"
	api_list = "http://de.netbase.pannous.com/json/short/"
	api_all = "http://de.netbase.pannous.com/json/query/all/"

# api = "http://localhost:8181/json/all/"
api_html = api.replace("json", "html")
api_limit = 1000
caches_netbase_ = expanduser("~/Library/Caches/netbase/")
abstracts_netbase = expanduser("~/Library/Caches/netbase/all/")


def cached_names():
	cached_files = ls(
		"~/Library/Caches/netbase/").map(lambda x: x.replace(".json", "").replace(" ", "_"))
	cached_files = cached_files.filter(lambda x: not is_number_string(x))
	return list(set(cached_files + cache.keys() + ['OKAH']))


if not os.path.exists(abstracts_netbase):
	os.makedirs(abstracts_netbase)  # mkdir


def download(url):  # to memory
	return urlopen(url).read()


def spo(edge):
	subject, predicate, object = edge['subject'], edge['predicate'], edge['object']
	return subject, predicate, object


def spo_ids(edge):
	sid, pid, oid = edge['sid'], edge['pid'], edge['oid']
	return sid, pid, oid


class Edges(extensions.xlist):
	def show(self):
		for edge in self:
			sid, pid, oid = edge['sid'], edge['pid'], edge['oid']
			subject, predicate, object = edge['subject'], edge['predicate'], edge['object']
			print("%d %d  %d  %s  %s  %s" %
					(sid, pid, oid, subject, predicate, object))


def get(id, name=0):
	return net.get(id or name)


class Node:
	def __init__(self, *args, **kwargs):
		if not kwargs:
			kwargs = args[0]
		self.loaded = False
		self.id = kwargs['id']
		self.name = kwargs['name']
		if 'topic' in kwargs:
			self.topic = kwargs['topic']
		if 'description' in kwargs:
			self.description = kwargs['description']
		else:
			self.description = ""
		if 'statementCount' in kwargs:
			self.count = kwargs['statementCount']
		if 'statements' in kwargs:
			self.edges = Edges(kwargs['statements'])
			self.loaded = True
		# self.statements = Edges(args['statements'])

	def print_csv(self):
		self.edges.show()

	def show_compact(self):
		print("%s{id:%d, topic:%s, edges=[" % (self.name, self.id, self.topic))
		for edge in self.edges:
			subject, predicate, object = edge['subject'], edge['predicate'], edge['object']
			predicate= predicate.replace(" ","_")
			if subject == self.name or edge['sid'] == self.id:
				print(" %s:%s," % (predicate, object))
			else:
				in_predicate = "_of" in predicate or "_after" in predicate or "_by" in predicate
				in_predicate = in_predicate or "_in" in predicate or "_von" in predicate
				if in_predicate:
					print(" %s:%s," % (predicate, subject))
				else:
					print(" %s_of:%s," % (predicate, subject))
		print("]}")

	def __dir__(self):
		return map(lambda x: x.replace(" ", "_"), self._predicates())

	def __str__(self):
		return self.name or self.id

	def __repr__(self):
		# return self._short()
		return self.name or self.id
	# return self.name + "_" + str(self.id)
	# if self.type:
	# 	return self.name + ":" + self.type.name
	# return self.name + ":" + self.type.name

	def _short(self):
		if self.topic:
			return "{name:'%s', id:%d, topic:'%s'}" % (self.name, self.id, self.topic)
		if not self.description:
			return "{name:'%s', id:%d}" % (self.name, self.id)
		return "{name:'%s', id:%d, description:'%s'}" % (self.name, self.id, self.description)

	def _json(self):
		return "{name:'%s', id:%d, description:'%s', statements:%s}" % (self.name, self.id, self.description, self.edges)

	def open(self):
		if "http" in self.name:
			os.system("open " + self.name)
		else:
			os.system("open " + api_html + self.name)

	def show(self):
		if "http" in self.name:
			os.system("open " + self.name)
		print(self.show_compact())
		# print(self._json())

	def _predicates(self):
		alles = []
		for e in self.edges:
			predicate = e['predicate']
			if not predicate in alles:
				alles.append(predicate)
		return xlist(set(alles))

	def _print_edges(self):
		for e in self.edges:
			if e['sid'] == self.id:
				print(" %s:%s" % (e['predicate'], e['object']))
			else:
				if " of" in e['predicate']:
					print(" %s: %s" %
							(e['predicate'].replace(" of", ""), e['subject']))
				else:
					print(" %s of: %s" % (e['predicate'], e['subject']))
		return self.edges

	def _map(self):
		map = {}
		for e in self.edges:
			if e['sid'] == self.id:
				map[e['predicate']] = e['object']
			else:
				if " of" in e['predicate']:
					map[e['predicate'].replace(" of", "")] = e['subject']
				else:
					map[e['predicate'] + " of"] = e['subject']
		return map

	def _load_edges(self):
		if self.loaded:
			return self.edges
		file = caches_netbase_ + str(self.id) + ".json"
		if not os.path.exists(file):
			url = api + str(self.id)
			print(url)
			urlretrieve(url, file)
		data = open(file,'rb').read()
		# data = codecs.open(file, "r", "utf-8").read()
		data = json.loads(data.decode('utf8', 'ignore'))  # FUCK PY3 !!!
		# data = json.loads(str(data, "UTF8"))  # FUCK PY3 !!!
		result = data['results'][0]
		self.edges = Edges(result['statements'])
		self.loaded = True
		return self.edges

	def fetchProperties(self,property):
		return download(api_all+self.name+"."+property)

	def getProperties(self, property, strict=False):
		if(self.statementCount>api_limit):
			return self.fetchProperties(property)
		found = []
		for e in self.edges:
			predicate = e['predicate'].lower()
			if predicate == property or not strict and (property in predicate):
				if e['sid'] == self.id:
					found.append(Node(name=e['object'], id=e['oid']))
				elif not strict:
					found.append(Node(name=e['subject'], id=e['sid']))
			if not strict and property in e['object']:
				found.append(Node(name=e['object'], id=e['sid']))
		if property == 'instance':
			found.extend(self.getProperties('type', strict=True))
		try:
			if self in found:
				found.remove(self)
		except Exception as ex:
			pass
		if not found:
			return xlist([])
		return xlist(found)

	# print(found)
	# return set(found)

	def getProperty(self, property, strict=False):
		if property == 'predicates':
			return self._predicates()
		if property == 'net':
			return net
		if property == 'edges':
			return self._load_edges()
		if property == 'all':
			return net._all(self.id, True, False)
		if property == 'list':
			return self._map()
		if property == 'count':
			return self.count or self.edges.count()
		if property == 'json':
			return self._json()
		if property == 'short':
			return self._short()
		if property == 'descriptions':
			return self.description

		property = property.replace("_", " ").lower()
		# print("getProperty " + self.name+"."+ property)
		for e in self.edges:
			predicate = e['predicate'].lower()
			if predicate == property:
				if e['sid'] == self.id:
					return Node(name=e['object'], id=e['oid'])
				elif not strict:
					return Node(name=e['subject'], id=e['sid'])
		if strict:
			return []#None
		for e in self.edges:
			if property in e['predicate'].lower():
				if e['oid'] == self.id:
					return Node(name=e['subject'], id=e['sid'])
				else:
					return Node(name=e['object'], id=e['oid'])
			if not strict and property in e['object']:
				return Node(name=e['object'], id=e['sid'])
		if property == 'parent':
			return self.getProperty('superclass', strict=True) or self.getProperty('type', strict=True)
		if is_plural(property):
			return self.getProperties(singular(property))

	def __getattr__(self, name):
		# print("get " + name)
		return self.getProperty(name)


# Node.show_edges = Node.print_csv
# Node._display = Node.show_compact
# Node._render = Node.show_compact
# Node._print = Node.show_compact


def is_plural(name):
	return name.endswith("s")  # todo


def singular(name):
	if name.endswith("ies"):
		return re.sub(r"ies$", "y", name)
	# return name.replace(r"ies$", "y")  # WTF PYTHON !
	if name.endswith("ses"):
		return re.sub(r"ses$", "s", name)
	if name.endswith("s"):
		return re.sub(r"s$", "", name)  # todo
	return name


class Netbase:
	def __init__(self):
		self.cache = {}
		self.caches = {}

	def types(self, name):
		return self._all(name, instances=False)

	# @classmethod
	def _all(self, name, instances=False, deep=False, reload=False):
		if isinstance(name, int):
			return self.get(name)
		# name = str(name)  # id
		if is_plural(name):
			return self._all(singular(name))
		if name in self.caches:
			return self.caches[name]
		file = abstracts_netbase + name + ".json"
		if reload or not os.path.exists(file):
			print(api + name)
			urlretrieve(api_all + name, file)
		data = codecs.open(file, "r", "utf-8").read()
		# data = open(file).read()
		try:
			data = json.loads(data)
		except Exception as ex:
			print(ex)
			os.remove(file)
			# return Node(id=-666, name="ERROR")
		nodes = extensions.xlist()
		for result in data['results']:
			# print(result)
			node = Node(result)
			nodes.append(node)
			if instances:
				nodes.append(self._all(node.id, False, True, reload))
				nodes.append(node.instances)
		self.caches[name] = nodes
		return nodes

	# @classmethod
	def get(self, name):
		# return all(name)[0]
		if isinstance(name, int):
			name = str(name)  # id
		if is_plural(name):
			return self._all(singular(name))
		if name in self.cache:
			return self.cache[name]
		# print("getThe "+name)

		file = caches_netbase_ + name + ".json"
		if not os.path.exists(file):
			print(api + name)
			urlretrieve(api + name, file)
		data = open(file, 'rb').read()
		# data = codecs.open(file, "r", "utf-8").read()
		try:
			data = json.loads(data.decode("UTF8", 'ignore'))  # FUCK PY3 !!!  'str' object has no attribute 'decode'
		except Exception as ex:
			print(ex)
			pass
		# os.remove(file)
		# noinspection PyTypeChecker
		results = data['results']
		if len(results) == 0:
			return None
		result = results[0]
		node = Node(result)
		self.cache[name] = node
		return node

	def __dir__(self):
		return cached_names()

	# return [] #  no autosuggest for root

	# def __call__(self):
	# 	return ['__call__ ??']

	def __getattr__(self, name):
		if name == "net":
			return net
		if name == "world":
			return net
		if name == "all":
			return All()  # use net.all.birds OR net.birds.all / net.bird.232.all
		# return self.all(name)
		# print("get "+name)
		return self.get(name)


class All(Netbase):
	def __getattr__(self, name):
		return self._all(name, False, False)

	# return self._all(name, True, True)


# return self._all(name, True, False) #reload


world = net = Netbase()
cache = net.cache
alle = All()


def main():
	# print(net.all.US)
	# print(net.united_states_of_america)
	# ps = str(net.winter.Part_of)
	# print(ps)
	print(world.california.show())
	print(world.california.parts)
	print(world.california.parts.count())
	print(world.california.parts.like("park"))
	print(world.california.parks)
	print(world.california.lakes)
	# print(world.california.parts.grep("river").unique())

	# print(world.california.open())
	# print(world.california.all.parks)
	# print(world.california.show_compact())
	# print(net.winter.show_compact())
	# print(world.california.synonym.id)
	return
	# print(net.c)
	# print(net.countries)
	# print(net.weapons)
	# print(net.states)


def test_states():
	print(net.states[0])
	print(net.states[0].description)
	print(net.states.descriptions)
	print(net.states[0].type)
	print(net.states[0].id)
	# print(net.states[0].subclasses)
	print(net.states[0].short)
	# print(net.california.open())
	# print(net.united_states_.edges.to_s())
	# print(net.united_states_.predicates)
	# print(net.united_states_.ofs)
	# print(alle.weapons)
	# print(net.north_america.countries)
	# print(net.north_america.predicates)
	# print(net.north_america.parts)
	# print(net.north_america.rocky_mountains_)
	print(net.rocky_mountains_.list)

	# print(net.north_america.states)

	# print(alle.insects)
	# print(net.id_10017)
	# print(net.types('country').id)
	#
	return
	print(net.Germany.name)
	print(net.Germany.capital)
	# print(net.Germany.edges)
	# print(net.Germany.predicates)
	print(net.Germany.type)
	print(net.Germany.saint)
	print(net.Germany.borders)
	print(net.Germany.time_zone)
	print(net.Germany.country_code)
	# print(net.Germany.image)
	print(net.Germany.flag.image)


# print(net.Germany.born.edges)

if __name__ == '__main__':
	main()
