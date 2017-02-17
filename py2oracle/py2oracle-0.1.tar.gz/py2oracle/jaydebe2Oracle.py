'''
Ver 20160721 by Jian: init version to test conn to oracle and teradata as "tstJDB.py" under C:\Users\daij12\Documents\Coldz\py\
Ver 20170216.1 by Jian: recap, and branch oracle to this script
assumptions: py2.X, jpype, jaydebeapi
Ver 20170216.2 by Jian: use pandas to convert query result to data frame
Ver 20170216.3 by Jian: packaging
note : there is a change in jaydebeapi connect interface, ref https://pypi.python.org/pypi/JayDeBeApi/
'''

def conn(jdbcFolder,url,user,pswd):
	import os
	os.environ['JAVA_HOME'] = jdbcFolder
	import jpype
	jpype.startJVM(jpype.getDefaultJVMPath(), '-Djava.class.path='+jdbcFolder+'/ojdbc6.jar')
	import jaydebeapi
	print user
	print pswd
	print url
	conn = jaydebeapi.connect('oracle.jdbc.OracleDriver','jdbc:oracle:thin:@'+url, [user, pswd])
	return conn.cursor()


def q(curs,qStr):
	curs.execute(qStr)
	return curs.fetchall()

