import os
from Jalapeno.lib import themeMgr
from Jalapeno.core import app
from flask import url_for
from Jalapeno.utils.config import config
'''
	This file is going to manage the theme
	get the templates and static
	push static dict to asset
'''


theme_name = config['Theme']
theme = themeMgr.Theme(theme_name)

app.static_folder = theme.static_path()
app.template_folder = theme.template_path()


@app.context_processor
def theme_processor():
	
	assets = theme.static_url_for()
	
	return dict(asset=assets)
