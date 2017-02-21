import yaml


def write(file, data):
	with open(file,'w') as yam:
		yaml.dump(data,yam, default_flow_style=False)

def read(file):
	with open(file,'r') as yam:
		return next(yaml.load_all(yam))