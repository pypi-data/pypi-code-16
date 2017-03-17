import time
from os import stat

def fileage(trgfile):
	return int(int(time.time())-int(stat(trgfile).st_mtime))
