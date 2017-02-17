'''
Ver 20160721 by Jian: init version to test conn to oracle and teradata as "tstJDB.py" under C:\Users\daij12\Documents\Coldz\py\
Ver 20170216.1 by Jian: recap, and branch oracle to this script
assumptions: py2.X, jpype, jaydebeapi
Ver 20170216.2 by Jian: use pandas to convert query result to data frame
Ver 20170216.3 by Jian: packaging
note : there is a change in jaydebeapi connect interface, ref https://pypi.python.org/pypi/JayDeBeApi/
'''

def conn(url,user,pswd,jdbcFolder=None,jdbcFileName=None):
	'''
		function to set up DB connection
		url:
		user:
		pswd:
		jdbcFolder:
		jdbcFileName:
		return a DB connector object
	'''
	# Experimental code BEGIN
	#import sys
	#print sys.modules[__name__]
	#<module 'py2oracle.jaydebe2Oracle' from 'C:\Python27\lib\site-packages\py2oracle\jaydebe2Oracle.pyc'>
	# Experimental code END

	import py2oracle
	if jdbcFolder is None:
		jdbcFolder = py2oracle.__path__[0] + '/jar'
	import os
	os.environ['JAVA_HOME'] = jdbcFolder
	import jpype
	if jdbcFileName is None:
		jdbcFileName='ojdbc6.jar'
	jpype.startJVM(jpype.getDefaultJVMPath(), '-Djava.class.path='+jdbcFolder+'/'+jdbcFileName)
	import jaydebeapi
	conn = jaydebeapi.connect('oracle.jdbc.OracleDriver','jdbc:oracle:thin:@'+url, [user, pswd])
	return conn.cursor()


def q(curs,qStr):
	'''
		function to run query
		curs: DB connector object
		qStr: query string
		return query result as a list of tuples
	'''
	curs.execute(qStr)
	return curs.fetchall()

