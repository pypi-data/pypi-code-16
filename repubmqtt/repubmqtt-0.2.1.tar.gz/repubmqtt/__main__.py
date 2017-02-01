#!/usr/bin/python3
import logging
import os
import paho.mqtt.client as mqtt
import repubmqtt
import json
import sys
import time
import requests
import pprint
import argparse
import traceback


DBG = 0

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	if DBG >= 1: logger.debug("MQTT connect, code "+str(rc))

	for topic in client.topics:
		client.subscribe(topic)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):

	pl = msg.payload.decode('utf-8')
	if DBG >= 1: logger.debug("%s  %s", msg.topic, pl)
	try:
		jrecord = json.loads(pl)
		if type(jrecord) != type({}):
			jrecord = None
	except Exception as e:
		jrecord = None

	if not jrecord:
		jrecord = {'rawvalue': pl}
		if DBG >= 2: logger.debug("payload not json '%s':  %s %s", e, msg.topic, pl)
	jrecord['topic'] = msg.topic
	userdata.process_message(jrecord)


def publish_mqtt(publish, output_data, data):
	topic = publish['topic'] % data
	retain = publish.get('retain',False)
	if publish['_testmode']:
		logger.info('testmode: publish_mqtt %s %s', topic, output_data)
		return
	client.publish(topic, output_data, retain=retain)


restful_cache = {}
def publish_restful(publish,  output_data, data):
	url = publish['url'] % data
	headers = publish['headers']
	if publish['_testmode']:
		logger.info('testmode: publish_restful (%s) %s', url, output_data)
		return

	now = time.time()
	if not url in restful_cache or (restful_cache[url]['ts'] + 60) < now:
		rsession = {}
		restful_cache[url] = rsession
		rsession['sess'] = requests.Session()
		rsession['ts'] = now
	else:
		rsession = restful_cache[url]
	sess = rsession['sess']
	response = sess.post(url, data=output_data, headers=headers)


def getargs():
	parser = argparse.ArgumentParser()
	parser.add_argument("-l", "--log", help="set loglevel, default is info")
	parser.add_argument("-t", "--topic", help="MQTT topics to listen of", action="append")
	parser.add_argument("-T", "--testmode", help="run in testmode", action="store_true")
	parser.add_argument("-v", "--verbose", help="produce verbose output", action="store_true")
	parser.add_argument("-X", "--debug", help="increase debug level",
					default=0, action="count")
	parser.add_argument("conf", help="config file to use", nargs='?', default=None)
	parser.add_argument("-d", "--datafile", help="data file to use", nargs=1)

	return parser.parse_args()


NONO = ['compile', 'exec', 'open', '__import__']
def makebuiltins():
	builtins = dict(__builtins__)
	for m in NONO:
		del builtins[m]
	return builtins


def load_conf(conf_global, conf_local, filename):
	try:
		exec(open(filename).read(), conf_global, conf_local )
	except Exception as e:
		print("error: load of config failed: %s" % e)
		return 1
	return 0


def check_conf(conf_local, NAMES, filename):
	err = 0

	for name in NAMES:
		if not name in conf_local:
			print("required entry '%s' missing in config file '%s'" % (name, filename))
			err = 1
	return err


def runtests(repub, testdata):
	err = 0
	for l in testdata:
		l = l.rstrip('\n')
		if len(l.lstrip()) == 0 or l.lstrip()[0] == "#":
			continue

		topic, msg = l.lstrip().split(None,1)
		try:
			jrecord = json.loads(msg)
		except Exception as e:
			jrecord = {'rawvalue': msg }
			if DBG: logger.debug("payload not json '%s':  %s", e, str(msg))
			err = 1
		jrecord['topic'] = topic
		pprint.pprint(jrecord)
		repub.process_message(jrecord)
	return err


#
#

REQUIRED_NAMES = [ 'RULES', 'XLATE']

REQUIRED_NAMES_RUN = ['MQTT_SERVER', 'MQTT_PORT', 'MQTT_CLIENT_ID', 'MQTT_USERNAME',
	'MQTT_PASSWORD', 'TOPICS', 'RULES', 'XLATE']

def main():
	global logger, DBG, client
	cl_args = getargs()

	if not cl_args.log:
		if cl_args.debug > 0:
			loglevel = logging.DEBUG
		else:
			loglevel = logging.INFO
	else:
		try:
			loglevel = getattr(logging, cl_args.log.upper())
		except Exception as e:
			print("invalid logging level %s, use debug, info, warning, error or critical")
			sys.exit(1)

	log_format='%(asctime)s %(levelname)s: %(message)s'
	log_datefmt='%Y-%m-%d %H:%M:%S'
	log_name = 'repub'
	logging.basicConfig(level=loglevel, format=log_format, datefmt=log_datefmt)
	logger = logging.getLogger(log_name)

	if cl_args.datafile:
		datafile = cl_args.datafile[0]
	else:
		datafile = None


	# setup the global namspace
	conf_global={'__builtins__': makebuiltins() }
	conf_global['logger'] = logger
	conf_global['sys'] = sys
	# setup the local namspace
	conf_local = {}
	conf_local['DBG'] = 0
	publishers = []
	# if a .rc file exists, load it into the local namespace
	if os.path.exists(os.path.expanduser("~/.repubmqttrc")):
		if load_conf(conf_global, conf_local, os.path.expanduser("~/.repubmqttrc")) != 0:
			return 1
		if 'PUBLISHERS' in conf_local:
			publishers += conf_local['PUBLISHERS']
			

	# load comand line config file into local namespace
	if cl_args.conf:
		if load_conf(conf_global, conf_local, cl_args.conf) != 0:
			return 1

	if not 'RULES' in conf_local:
		conf_local['RULES'] = []
	if not 'XLATE' in conf_local:
		conf_local['XLATE'] = {}

	if check_conf(conf_local, REQUIRED_NAMES, cl_args.conf) != 0:
		return 1

	DBG = cl_args.debug if cl_args.debug > 0 else conf_local['DBG']
	testmode = conf_local.get('TESTMODE', False) or cl_args.testmode

	repub = repubmqtt.Republish(conf_local['RULES'], conf_local['XLATE'], log_name)
	repub.setdebuglevel(DBG)
	repub.settestmode(testmode)

	repub.register_publish_protocol('mqtt', publish_mqtt)
	repub.register_publish_protocol('restful', publish_restful)
	for p, pf in publishers:
		repub.register_publish_protocol(p, pf)

	if testmode:
		if not datafile and not 'TESTDATA' in conf_local:
			print("error: testmode requires --datafile or TESTDATA list in conf file")
			sys.exit(1)
		testdata = []
		if datafile:
			try:
				testdata += open(datafile, "r").readlines()
			except Exception as e:
				print("error: failed to load testdata: %s" % e)
				sys.exit(1)
		else:
			testdata += conf_local['TESTDATA']


#		exec(conf_local['test1'], conf_global, conf_local)(1)
#		try:
#			conf_local['test1']('jjjj')
#		except Exception as e:
#			print(e, traceback.format_exc(limit=None))
#		return 0

		return runtests(repub, testdata)
	else:
		if cl_args.topic:
			conf_local['TOPICS'] = conf_local.get('TOPICS',[]) + cl_args.topic

		if check_conf(conf_local, REQUIRED_NAMES_RUN, cl_args.conf) != 0:
			return 1

		client = mqtt.Client(client_id=conf_local['MQTT_CLIENT_ID'], userdata=repub)
		client.topics = conf_local['TOPICS']
		client.username_pw_set(conf_local['MQTT_USERNAME'], conf_local['MQTT_PASSWORD'])
		client.on_connect = on_connect
		client.on_message = on_message

		client.connect(conf_local['MQTT_SERVER'], conf_local['MQTT_PORT'], 60)
		client.loop_forever()
		return 0


if __name__ == "__main__":

	sys.exit(main())
