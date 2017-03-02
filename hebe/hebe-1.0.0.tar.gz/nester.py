"""This is the "nester.py" module and it provides one function called hebe which
prints lists that may or may not include nested list"""
def hebe(the_list):
	for each_item in the_list:
		if isinstance(each_item,list):
			hebe(each_item)
		else:print(each_item)
