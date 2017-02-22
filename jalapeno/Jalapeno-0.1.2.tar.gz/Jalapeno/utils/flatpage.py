from flask_flatpages import FlatPages
from Jalapeno.core import app
import os
from Jalapeno.utils.config import config
from Jalapeno.lib.jalop_markdown import Jalop_markdown
from Jalapeno.path import APP_DIR


flatpage_source = APP_DIR+os.sep+'Jalapeno'+os.sep+'Pages'


sitepages = {}

flatpage_mods = ['markpages']
for pagetype in config['views']:	
	if pagetype in ['posts'] or pagetype in ['docs']:
		flatpage_mods.extend(config['views'][pagetype])	
for each in flatpage_mods:
	flat = FlatPages(app,name=each)
	sitepages[each]=flat

	flatpage_folder = os.path.join(flatpage_source,each)
	if not os.path.exists(flatpage_folder):
		print("creating folder",each)
		os.mkdir(flatpage_folder)
	else:
		pass
	each = each.upper()
	app.config['FLATPAGES_%s_MARKDOWN_EXTENSIONS'%each] = ['codehilite','tables','toc','markdown.extensions.meta']
	app.config['FLATPAGES_%s_ROOT'%each] = flatpage_folder
	app.config['FLATPAGES_%s_EXTENSION'%each] = '.md'
	app.config['FLATPAGES_%s_HTML_RENDERER'%each] = Jalop_markdown
	
	




