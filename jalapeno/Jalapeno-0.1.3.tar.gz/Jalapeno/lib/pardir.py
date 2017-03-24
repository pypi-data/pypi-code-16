import os

def par_dir():
	return os.path.join(os.path.join(os.path.dirname(__file__),os.path.pardir),os.path.pardir)


def no_dot(path):
	path=path.split('/')
	newpath=[]
	for each in path:
		if each =='..':
			newpath=newpath[:-1]
		else:
			newpath.append(each)
	return '/'.join(newpath)