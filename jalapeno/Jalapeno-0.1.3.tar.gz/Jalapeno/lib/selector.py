'''This module includes the function to create different flatpages and views'''

def flatpage_filter(rule,config):
	ret = False
	hold = []
	for k,v in config['views'].items():
		for key,value in v.items():
			if rule in value[0] and isinstance(value[0],list):
				hold.append(key)
			elif rule in value:
				hold.append(key)
	if len(hold) != 1:
		print("Duplicate url or None")
		print(hold)
	else:
		postsname = hold[0]
	
	return postsname

def view_register(L,blueprint,func):
	for each in L:
		if isinstance(each[0],list):

			for ea in each[0]:

				blueprint.add_url_rule(ea,each[1],func)
		else:
			blueprint.add_url_rule(each[0],each[1],func)
			
def get_template(L,rule):
	template=None
	for each in L:
		if rule in each[0] or rule in each:
			template = each[2]
			return template
	if not template:
		return '404.html'