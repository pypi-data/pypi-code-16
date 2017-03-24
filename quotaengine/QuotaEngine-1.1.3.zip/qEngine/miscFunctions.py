def merge_dicts(*dict_args):
	"""
	Given any number of dicts, shallow copy and merge into a new dict,
	precedence goes to key value pairs in latter dicts.
	"""
	result = {}
	for dictionary in dict_args:
		result.update(dictionary)
	return result

def prod(lst):
	res = 1
	for i in lst:
		res = res*i
	return res

def combineLists(lst, delim='\n'):
	try:
		if type(lst[0]) is not list:
			return lst
		elif len(lst) == 1:
			return lst[0]
		else:
			newlst = combineLists(lst[:len(lst) - 2] + [['{elem1}{delim}{elem2}'.format(elem1=i,elem2=j,delim=delim) for i in lst[len(lst) - 2] for j in lst[len(lst) - 1]]])
			return newlst
	except IndexError:
		return lst