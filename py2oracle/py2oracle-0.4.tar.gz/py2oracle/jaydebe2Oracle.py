'''
Ver 20160721 by Jian: init version to test conn to oracle and teradata as "tstJDB.py" under C:\Users\daij12\Documents\Coldz\py\
Ver 20170216.1 by Jian: recap, and branch oracle to this script
assumptions: py2.X, jpype, jaydebeapi
Ver 20170216.2 by Jian: use pandas to convert query result to data frame
Ver 20170216.3 by Jian: packaging
note : there is a change in jaydebeapi connect interface, ref https://pypi.python.org/pypi/JayDeBeApi/
Ver 20170218 by Jian: oo-ing
'''

class Cur:
	def __init__(_,url,user,pswd,jdbcFolder=None,jdbcFileName=None):
		import py2oracle
		if jdbcFolder is None:
			_.jdbcFolder = py2oracle.__path__[0] + '/jar' # assume the path structure
		else:
			_.jdbcFolder = jdbcFolder
		if jdbcFileName is None:
			_.jdbcFileName='ojdbc6.jar' # assume file name
		else:
			_.jdbcFileName=jdbcFileName
		_.url=url
		_.user=user
		_.pswd=pswd
		import os
		os.environ['JAVA_HOME'] = _.jdbcFolder
		import jpype
		jpype.startJVM(jpype.getDefaultJVMPath(), '-Djava.class.path='+_.jdbcFolder+'/'+_.jdbcFileName)
		import jaydebeapi
		_.conn = jaydebeapi.connect('oracle.jdbc.OracleDriver','jdbc:oracle:thin:@'+_.url, [_.user, _.pswd])
		_.cursor=_.conn.cursor()


	def q(_,qStr):
		_.cursor.execute(qStr)
		return _.cursor.fetchall()
	def __del__(_):
		print 'wrap up'
		_.cursor.close()
		_.conn.close()

