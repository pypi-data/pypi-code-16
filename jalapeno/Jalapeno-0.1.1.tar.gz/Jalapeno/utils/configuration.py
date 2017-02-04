from Jalapeno import app
import os
from Jalapeno.path import path
import yaml




config_path = path()+os.sep+'Jalapeno'+os.sep+'Profile'+os.sep+'_config.yaml'
config_content=open(config_path,'r').read()

config = yaml.load(config_content)
config_flatpage = path()+os.sep+'Jalapeno'+os.sep+'configuration'

app.config.from_pyfile(config_flatpage+os.sep+'_config.py')



