# This is a tool to read and write quasselcore configuration files.
## Currently a major WIP.

import argparse
import os
import sys
import tempfile

# Depend on PyQt5 and QtCore.
from PyQt5 import QtCore, QtGui

def getConfigFilename(directory, filetype):
	"""	 Returns the path to the configuration file, None if no file exists."""
	filename = None

	if filetype == "core":
		filename = os.path.join(directory, "quasselcore.conf")
	elif filetype == "client":
		filename = os.path.join(directory, "quasselclient.conf")
	elif filetype == "mono":
		filename = os.path.join(directory, "quassel.conf")

	if not filename is None and not os.path.exists(filename):
		filename = None

	return filename

def main():
	parser = argparse.ArgumentParser(description="Tool to manipulate quassel config files.")
	parser.add_argument("-c", "--config-dir", dest="cfgdir", default="/var/lib/quassel/", help="Config directory, defaults to /var/lib/quassel/")
	parser.add_argument("-t", "--type", dest="filetype", default="core", help="Config file to read, either 'core' (default), 'client', or 'mono'.")
	
	args = parser.parse_args()
	
	# Make sure the filename is valid.
	filename = getConfigFilename(os.path.abspath(args.cfgdir), args.filetype)
	if filename is None:
		print("Please pass -t ('core'|'client'|'mono') and make sure the file exists in the specified directory.")
		sys.exit(1)
	
	# Load the file, parse all of the keys into a dictionary.
	processed = {}
	settings = QtCore.QSettings(filename, QtCore.QSettings.IniFormat)
	for key in settings.allKeys():
		processed[key] = str(settings.value(key))

	# Now, create a new config file in a temporary file and then print it out.
	tempname = tempfile.mkstemp()[1]
	newSettings = QtCore.QSettings(tempname, QtCore.QSettings.IniFormat)
	for key, value in processed.items():
		newSettings.setValue(key, value)
	newSettings.sync()
	
	# Now, print that new file to terminal and delete it.
	with open(tempname, 'r') as newSettingsFile:
		print(newSettingsFile.read())
	os.remove(tempname)
	
if __name__ == '__main__':
	main()
