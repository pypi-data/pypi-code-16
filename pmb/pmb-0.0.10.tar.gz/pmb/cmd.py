import subprocess
import sys

def executeCommand(cmd):
	try:
		if not( isinstance(cmd, str) ):
			cmd = str(cmd, "utf-8")
		cmd = cmd.rstrip()
		print( "Executing command \"" + cmd + "\"" )
		proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
		(out, err) = proc.communicate()
		print( "Return code: ", proc.returncode ) # 0 => SUCCESS, >0 => ERROR
		if err:
			print( "Error: \n", err.strip() )
			print( "Error> error ", err.strip() )
		if out:
			print( "Output: \n", str( out, "utf-8") )
			return out
		if proc.returncode!=0:
			raise RuntimeError( "Command exited with return code " + str( proc.returncode ) )
	except ValueError as e:
		print( "ValueError: ", e.returncode )
		print( "ValueError: ", e.output )
	except OSError as e:
		print( "OSError: ", e.errno )
		print( "OSError: ", e.strerror )
		print( "OSError: ", e.filename )