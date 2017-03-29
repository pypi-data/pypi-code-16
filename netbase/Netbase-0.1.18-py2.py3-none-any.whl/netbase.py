#!/usr/bin/env PYTHONIOENCODING="utf-8" python
# -*- coding: utf-8 -*-
import os
import re
import locale
import os.path
import json
import codecs  # codecs.open(file, "r", "utf-8")

# import dill as pickle  # BEST! no more Can't pickle <function
# from units import unit

from os.path import expanduser
try:  # pathetic python3 !
	from urllib2 import urlopen
	from urllib import urlretrieve
except ImportError:
	from urllib.request import urlopen, urlretrieve  # library HELL

from extensions import *  # for functions
import extensions
from relations import Relations
from relations import Relations as R

# print R.mro()
api_limit = 1000

# api = "http://localhost:8181/json/all/"

domain="http://netbase.pannous.com"

lang ="" # en default
if "de" in locale.getdefaultlocale() or 'GERMAN' in os.environ:
	lang="de"
	print("GERMAN!")
	# domain = "http://dev.netbase.pannous.com:81"
	# domain = "http://de.netbase.pannous.com:81"
	domain = "http://87.118.71.26:81" # q.big

api = domain+"/json/all/"
api_list = domain+"json/short/"
api_all = domain + "/json/query/all/"
api_query_short = domain + "/json/short/query/"
"""http://87.118.71.26:81/short/query/germany.hauptstadt"""

api_html = api.replace("json", "html")

file_caches = expanduser("~/Library/Caches/netbase/")
abstracts_cache = expanduser("~/Library/Caches/netbase/all/")
file_caches += lang + "/"
abstracts_cache += lang + "/"
# if CLEAR CACHE
CLEAR_CACHE = False
if CLEAR_CACHE and os.path.exists(file_caches):
	shutil.rmtree(file_caches)
if CLEAR_CACHE and os.path.exists(abstracts_cache):
	shutil.rmtree(abstracts_cache)
if not os.path.exists(abstracts_cache):
	os.makedirs(abstracts_cache)  # mkdir
if not os.path.exists(file_caches):
	os.makedirs(file_caches)  # mkdir


def cached_names():
	return []
	# cached_files = ls(
	# 	"~/Library/Caches/netbase/").map(lambda x: x.replace(".json", "").replace(" ", "_"))
	# cached_files = cached_files.filter(lambda x: not is_number_string(x))
	# return list(set(cached_files + cache.keys() + ['OKAH']))




def download(url):  # to memory
	return urlopen(url).read()


def spo(edge):
	subject, predicate, object = edge['subject'], edge['predicate'], edge['object']
	return subject, predicate, object


def spo_ids(edge):
	sid, pid, oid = edge['sid'], edge['pid'], edge['oid']
	return sid, pid, oid

class Todo(Exception):
	pass

def query(edges):
	return net.get(edges,api=api_query_short)



class Edges(extensions.xlist):

	def show(self):
		for edge in self:
			sid, pid, oid = edge['sid'], edge['pid'], edge['oid'] # sid=subject_id ...
			subject, predicate, object = edge['subject'], edge['predicate'], edge['object']
			print("%d %d  %d  %s  %s  %s" %
					(sid, pid, oid, subject, predicate, object))

	def of(self,property):
		# if self.complete:
		self.filter(lambda x:x.has(property))
		# else:
		# 	query(self.name+"."+property)

	# def with keyword:(
	# def list(self):

	# all.cities>1000km
	# all.cities>1000*people
	def __gt__(self, other):
		return query(self.name+">"+other)


def get(id, name=0):
	return net.get(id or name)

class SelectProxy:
	def __init__(self, node):
		self.node=node

	def __getattr__(self, item):
		return self.node.getProperty(item)


Any= 'any' # sentinel

class Node:
	def __init__(self, *args, **kwargs):
		if not kwargs:
			kwargs = args[0]
		self.loaded = False
		self.id = kwargs['id']
		self.name = kwargs['name']
		self.is_abstract= 'kind' in kwargs and kwargs['kind'] == -102
		self.topic = 'topic' in kwargs and kwargs['topic'] or None
		if 'description' in kwargs:
			self.description = kwargs['description']
		else:
			self.description = ""
		if 'statementCount' in kwargs:
			self.count = kwargs['statementCount']
		if 'value' in kwargs:
			self.value=kwargs['value']
		if 'statements' in kwargs:
			self.edges = Edges(kwargs['statements'])
			self.loaded = True
		# self.statements = Edges(args['statements'])

	def __eq__(self, other):
		if isinstance(other, list):
			other = other[0]
		if isinstance(other, int):
			return other == self.id
		if isinstance(other, str):
			return other.lower() == self.name.lower()
		if isinstance(other, Node):
			return other.id == self.id or other.name.lower() == self.name.lower()
		return False

	def has(self,property, object=Any):
		for e in self.edges:
			if e['pid']==property:
				return object==Any or object == e['oid']

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
		if self.topic:
			return "%s(%s)%s" % (self.name, self.topic, self.is_abstract and "*" or "")
		if self.name and self.id:
			return "%s(%d)%s" % (self.name, self.id, self.is_abstract and "*" or "")
		return self.name or self.id

	def __repr__(self):
		return self._short()
		# return self.name or self.id
	# return self.name + "_" + str(self.id)
	# if self.type:
	# 	return self.name + ":" + self.type.name
	# return self.name + ":" + self.type.name

	def _short(self):
		if self.topic:
			return "{name:'%s', id:%d, topic:'%s'}" % (self.name, self.id, self.topic)
		if not self.description:
			return "{name:'%s', id:%s%d}" % (self.name, self.is_abstract and "+" or "", self.id)
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
		file = file_caches + str(self.id) + ".json"
		if not os.path.exists(file):
			url = api + str(self.id)
			print(url)
			urlretrieve(url, file)
		# data = open(file,'rb').read()
		data = codecs.open(file, "r", "utf-8").read()
		if py2: data=data.decode('utf8', 'ignore')
		data = json.loads(data)  # FUCK PY3 !!!
		# data = json.loads(str(data, "UTF8"))  # FUCK PY3 !!!
		results = data['results']
		if len(results)==0:
			return []
		result = results[0]
		self.edges = Edges(result['statements'])
		self.loaded = True
		return self.edges

	def fetchProperties(self,property):
		return download(api_all+self.name+"."+property)

	def getProperties(self, property, strict=False):
		# if(self.statementCount>api_limit):
		# 	return self.fetchProperties(property)
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
		if property == 'properties':
			return self._predicates()
		if property == 'net':
			return net
		if property == 'select':
			return SelectProxy(self)
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
			object_ = e['object'].lower()
			if property in e['predicate'].lower():
				if e['oid'] == self.id:
					return Node(name=e['subject'], id=e['sid'])
				else:
					return Node(name=object_, id=e['oid'])
			if not strict and property in object_:
				return Node(name=object_, id=e['sid'])
		if property == 'parent':
			return self.getProperty('superclass', strict=True) or self.getProperty('type', strict=True)
		if is_plural(property):
			return self.getProperties(singular(property))
		if self.is_abstract and property!='instance':
			for i in self.instances:
				p=i.getProperty(property)
				if p: return p
		return query(str(self.id)+"."+property) or query(str(self.name)+ "." + property)

	def __getattr__(self, name):
		# print("get " + name)
		return self.getProperty(name)

	def reload(self):
		return net.get(self.id or self.name, False, False)


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


def find_best(nodes):
	if isinstance(nodes, str): nodes = net._all(nodes)
	if not isinstance(nodes,list): nodes=[nodes]
	abstract=nodes[0]
	best = 0
	for n in nodes:
		if n.is_abstract:
			abstract=n
		else:
			best= n
			break # first is best via webserver
	if not best:
		for n in abstract.instances:
			maxi=n.statementCount
			if maxi>max0:
				max0=maxi
				best=n
	if not best:
		for n in abstract.labels:
			maxi = n.statementCount
			if maxi > max0:
				max0 = maxi
				best = n
	if best:
		net.the_cache[abstract.name] = best
		abstract.main=best
		return best



class Netbase:
	def __init__(self):
		self.cache = {} # abstracts
		self.the_cache={} # best
		self.caches = {} # lists

	def types(self, name):
		return self._all(name, instances=False) # select(kind=...)

	# @classmethod
	def _all(self, name, instances=False, deep=False, reload=False):
		if isinstance(name, int):
			n=self.get(name)
			if not n.is_abstract: return n
			else: name = str(name)  # id
		if is_plural(name):
			return self._all(singular(name))
		if name in self.caches:
			return self.caches[name]
		file = abstracts_cache + name + ".json"
		if reload or not os.path.exists(file):
			print(api + name)
			urlretrieve(api_all + name, file)
		# data = codecs.open(file, "r", "utf-8", errors='ignore').read()
		# data = open(file,'rb').read()
		data = open(file).read()
		if not isinstance(data,unicode) and not isinstance(data,str):
			data=data.decode("UTF8", 'ignore')
		# FUCK PY3 !!!  'str' object has no attribute 'decode'
		# 	FUCKING PYTHON MADNESS!!
		# http://stackoverflow.com/questions/5096776/unicode-decodeutf-8-ignore-raising-unicodeencodeerror#5096928
		try:
			# data = json.loads(data)
			data = json.loads(data)
		except Exception as ex:
			print(ex)
			os.remove(file)
			# return Node(id=-666, name="ERROR")
		nodes = extensions.xlist()
		# noinspection PyTypeChecker
		for result in data['results']:
			# print(result)
			node = Node(result)
			nodes.append(node)
			if instances:
				nodes.append(self._all(node.id, False, True, reload))
				nodes.append(node.instances)
		self.caches[name] = nodes
		find_best(nodes)
		return nodes

	# @classmethod
	def get(self, name, get_the=False,use_cache=True, api=api):
		# return all(name)[0]
		if isinstance(name, int):
			name = str(name)  # id
		# else: get_the or abstract !
		if is_plural(name):
			return self._all(singular(name))
		if use_cache:
			if get_the and name in self.the_cache:
					return self.the_cache[name]
			if name in self.cache:
					node= cache[name]
					# if get_the and not node.is_abstract:
					# 	return node.the
					return node
			if name in self.caches:
				node=self.caches[name][0]
				if node.is_abstract:
					self.cache[name]=node
				else:
					self.the_cache[name]=node
				return node
		file = file_caches + name + ".json"
		if not use_cache or not os.path.exists(file):
			print(api + name)
			try:
				urlretrieve(api + name, file)
			except:
				print(api+name)
				raise
		# data = open(file, 'rb').read()
		data = codecs.open(file, "rb", "utf-8").read()
		if not isinstance(data, unicode) and not isinstance(data, str):
			data = data.decode("UTF8", 'ignore')
		try:
			data = json.loads(data)  # FUCK PY3 !!!  'str' object has no attribute 'decode'
		except Exception as ex:
			print(api + name)
			print(data)
			print(ex)
			os.remove(file)
			raise
		# os.remove(file)
		# noinspection PyTypeChecker
		results = data['results']
		if len(results) == 0:
			return None
		for i in range(len(results)):
			result = results[i] # first == 'the'
			node = Node(result)
			if not get_the or not node.is_abstract: break
		if node.is_abstract:
			self.cache[name] = node
		else:
			self.the_cache[name] = node
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
			return alle  # use net.all.birds OR net.birds.all / net.bird.232.all
		# return self.all(name)
		# print("get "+name)
		return self.get(name)


class Alle(type):
	def __getattr__(self, name):
		return net._all(name, False, False)


class Alles(Netbase):
	def __getattr__(self, name):
		return net._all(name, False, False)



class The:
	def __getattr__(self, name):
		return net.get(name, get_the=True)


if py2:
	class All:
		__metaclass__ = Alle
else:
	try:
		from .alle import All# fuck py3
	except Exception as err:
		from alle import All  # fuck py3

world = net = Netbase()
cache = net.cache
alle = Alles()
the = The()
if py3: All.setNet(net)


class Unit:
	def __init__(self, value=1.):
		self.value = value

	def __mul__(self, other):
		# self.value = self.value * other
		return Node(id=0,name=str(other)+ type_name(self),value=self.value * other)

class Km(Unit):
	def __eq__(self, other):
		return self.value == other.value


km = Km()
assert Km(3) == km * 3

def tests():
	assert find_best("germany").id== 183
	print(the.germany)
	print(the.germany.id)
	# print(the.germany.capital)
	print(the.germany.Hauptstadt)
	germany = the.germany.reload()
	print(germany.name)
	print(germany.description)
	print(germany.topic)
	print(germany.id)
	# print(germany.show())
	# print(the.germany.json)
	# print(All.germany)
	print(the.germany.capital)
	print(the.germany.properties)
	assert the.germany.capital=="Berlin" or the.germany.Hauptstadt=="Berlin"
	exit()


for r in dir(Relations):
	if "__" in r: continue
	rr = r.replace("_", "").capitalize()
	n = Node(id=Relations[r].value, name=rr)
	setattr(Relations, rr, n)


def main():
	if py3: All.setNet(net)
	tests()
	# print(the.USA)
	# print(All.hi)
	xs= All.USA
	for bad in xs:
		print (bad.id)
		print (bad.name)
		print (bad._short())
		print (bad.topic)
		print (bad.description)
	print(xs)
	# print(net.USA.all)
	# print(net.USA.select.country) # select proxy hack
	return

if __name__ == '__main__':
	main()
