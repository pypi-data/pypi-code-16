#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
import httplib
import md5
import urllib
import random
import getopt
import json

version = '1.0.6'
languages = '''auto     自动检测	Automatic Detection
zh	 中文		Chinese
en	 英语		English
yue	 粤语		Cantonese
wyw	 文言文		Classical Chinese
jp	 日语		Japanese
kor	 韩语		Korean
fra	 法语		French
spa	 西班牙语	Spanish
th	 泰语		Thai
ara	 阿拉伯语	Arabic
ru	 俄语		Russian
pt	 葡萄牙语	Portuguese
de	 德语		German
it	 意大利语	Italian
el	 希腊语		Greek
nl	 荷兰语		Dutch
pl	 波兰语		Polish
bul	 保加利亚语	Bulgarian
est	 爱沙尼亚语	Estonian
dan	 丹麦语		Danish
fin	 芬兰语		Finnish
cs	 捷克语		Czech
rom	 罗马尼亚语	Romanian
slo	 斯洛文尼亚语	Slovenian
swe	 瑞典语		Swedish
hu	 匈牙利语	Hungarian
cht      繁体中文	Traditional Chinese'''

def logo():
	print '                         _ _          _ _      _   '
	print ' _ __  _   _  ___  _ __ | (_) ___  __| (_) ___| |_ '
	print "| '_ \| | | |/ _ \| '_ \| | |/ _ \/ _` | |/ __| __|"
	print '| |_) | |_| | (_) | | | | | |  __/ (_| | | (__| |_ '
	print '| .__/ \__, |\___/|_| |_|_|_|\___|\__,_|_|\___|\__|'
	print '|_|    |___/                                       '

def usage():
	print 'Copyright (c) 2017 pyonlinedict ' + version + ' by sunnyelf'
	print 'Blog: https://www.hackfun.org'
	print 'Home: https://github/sunnyelf/pyonlinedict\n'
	print 'Usage: pyonlinedict [options]\n'
	print ' Options: '
	print '  -h, --help          Show help message and exit'
	print '  -q, --query         The word or sentence to be queried(required parameters)'
	print '  -f, --from          The type of the input language(default setting:auto)'
	print '  -t, --to            The type of the output language(default setting:zh)'
	print '  -l, --list          List the supported language types'
	print '  -v, --version       Displays the current version number and author information'
	print
	print ' Usages: '
	print '  pyonlinedict -h'
	print '  pyonlinedict -l'
	print '  pyonlinedict -v'
	print '  pyonlinedict -q hello'
	print '  pyonlinedict -q hello -f en -t zh'
	print "  pyonlinedict -q 'Hello world!' -f en -t zh"

def get_input():
	query,from_language, to_language = '','',''

	if len(sys.argv) == 1:
		logo()
		usage()
		sys.exit()

	try:
		opts, args = getopt.getopt(sys.argv[1:], "hlvq:f:t:", ["help", "list", "version", "query=","from=", "to="])

	except getopt.GetoptError, e:
		usage()
		print '\n[!] ' + str(e)
		sys.exit()

	if args:
		usage()
		print '\n[!] The input is incorrect,please refer to usage.'
		sys.exit()

	options=['-h','-l','-v','-q','-f','-t','--help','--list','--version','--query','--from','--to']
	for op,value in  opts:
		if op not in options:
			usage()
			print '\n[!] This option is nonexistent,please refer to usage.'
			sys.exit()
	
	for op,value in  opts:
		if '-f' not in op or '--from' not in op:
			from_language = 'auto'
		if '-t' not in op or '--to' not in op:
			to_language = 'zh'
	
	for op, value in opts:
			if op == '-q' or op == '--query':
					query = value
			elif op == '-f' or op == '--from':
					from_language = value
			elif op == '-t' or op == '--to':
					to_language = value
			elif op == '-h' or op == '--help':
					logo()
					usage()
					sys.exit()
			elif op == '-l' or op == '--list':
					print languages
					sys.exit()
			elif op == '-v' or op == '--version':
					print 'Copyright (c) 2017 pyonlinedict ' + version + ' by sunnyelf'
					sys.exit()
	
	return query,from_language,to_language

def translate(query, from_language, to_language):
	appid = '2015063000000001'
	secretKey = '12345678'
	httpClient = None
	myurl = '/api/trans/vip/translate'
	salt = random.randint(32768, 65536)
	sign = appid+query+str(salt)+secretKey
	m1 = md5.new()
	m1.update(sign)
	sign = m1.hexdigest()
	myurl = myurl+'?appid='+appid+'&q='+urllib.quote(query)+'&from='+from_language+'&to='+to_language+'&salt='+str(salt)+'&sign='+sign
	
	try:
		httpClient = httplib.HTTPConnection('api.fanyi.baidu.com')
		httpClient.request('GET', myurl)
		response = httpClient.getresponse()
		return response.read()
	except Exception, e:
		print e
	finally:
		if httpClient:
			httpClient.close()

def print_error_information(error_code,error_msg):
	print '[!] Oops,error code is: ' + error_code + ' and error message is: ' + error_msg

def output_process(result):
	tojson = json.loads(result)
	for key in tojson:
		if 'error_code' in key:
			if int(tojson['error_code']) == 52001:
				print_error_information(str(tojson['error_code']), str(tojson['error_msg']))
				print '[*] Request timed out'
				print '[>] Please try again'
				sys.exit()
			elif int(tojson['error_code']) == 52002:
				print_error_information(str(tojson['error_code']), str(tojson['error_msg']))
				print '[*] Server system error'
				print '[>] Please try again'
				sys.exit()
			elif int(tojson['error_code']) == 52003:
				print_error_information(str(tojson['error_code']), str(tojson['error_msg']))
				print '[*] Unauthorized user'
				print '[>] Please check your appid is correct'
				sys.exit()
			elif int(tojson['error_code']) == 54000:
				print_error_information(str(tojson['error_code']), str(tojson['error_msg']))
				print '[*] Required parameters are empty'
				print '[>] Please check whether fewer parameters'
				sys.exit()
			elif int(tojson['error_code']) == 54001:
				print_error_information(str(tojson['error_code']), str(tojson['error_msg']))
				print '[*] Signature error'
				print '[>] Please check your signature generation method'
				sys.exit()
			elif int(tojson['error_code']) == 54003:
				print_error_information(str(tojson['error_code']), str(tojson['error_msg']))
				print '[*] Access frequency is limited'
				print '[>] Please reduce your call frequency'
			elif int(tojson['error_code']) == 54004:
				print_error_information(str(tojson['error_code']), str(tojson['error_msg']))
				print '[*] The account balance is insufficient'
				print '[>] Please go to the management console to recharge the account'
				sys.exit()
			elif int(tojson['error_code']) == 54005:
				print_error_information(str(tojson['error_code']), str(tojson['error_msg']))
				print '[*] Request frequent'
				print '[>] Please reduce the long query send frequency, 3 seconds and try again'
				sys.exit()
			elif int(tojson['error_code']) == 58000:
				print_error_information(str(tojson['error_code']), str(tojson['error_msg']))
				print '[*] Client IP is illegal'
				print '[>] Please check whether you fill in the IP address is correct,you can modify the server IP address that you fill in'
				sys.exit()
			elif int(tojson['error_code']) == 58001:
				print_error_information(str(tojson['error_code']), str(tojson['error_msg']))
				print '[*] The translation direction is not supported'
				print '[>] Please check whether the target language is in the language list'
				sys.exit()
			else:
				print_error_information(str(tojson['error_code']), str(tojson['error_msg']))
				sys.exit()
	print '[->] ' + tojson['trans_result'][0]['dst']
def main():
	query,from_language,to_language = get_input()
	result = translate(query, from_language, to_language)
	output_process(result)


if __name__ == '__main__':
	main()
