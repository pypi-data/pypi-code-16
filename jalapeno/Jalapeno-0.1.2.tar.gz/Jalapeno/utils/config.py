from Jalapeno.core import app
import os
from Jalapeno.path import APP_DIR
import yaml


#Load Flatpage/View config

config_path = APP_DIR+os.sep+'Jalapeno'+os.sep+'_config'+os.sep+'_config.yaml'
config_content=open(config_path,'r').read()
config = yaml.load(config_content)



#Load general Settings
config_flatpage = APP_DIR+os.sep+'Jalapeno'+os.sep+'_config'
app.config.from_pyfile(config_flatpage+os.sep+'flask_settings.py')



#load profile
profile_path = APP_DIR+os.sep+'Jalapeno'+os.sep+'_config'+os.sep+'profile.yaml'
config['Jalo'] = yaml.load(open(profile_path,'r').read())


@app.context_processor
def profile_processor():
	
	me = config['Jalo']
	
	return dict(Jalo=me)