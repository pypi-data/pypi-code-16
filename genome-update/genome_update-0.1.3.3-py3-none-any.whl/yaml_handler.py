import yaml

class yaml_handler:

	def write(self, file, data):
		with open(file,'w') as yam:
			yaml.dump(data,yam)

	def read(self, file):
		with open(file,'r') as yam:
			return next(yaml.load_all(yam))