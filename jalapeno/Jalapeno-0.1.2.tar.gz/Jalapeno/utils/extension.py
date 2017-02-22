from Jalapeno.core import app
from flask import Blueprint,send_from_directory
import os
from Jalapeno.path import APP_DIR
from Jalapeno.lib.fileMgr import Mgr 
from Jalapeno.lib.url_for_builder import path_url_builder
from markupsafe import Markup


extension = Blueprint('extension',__name__)

extension_path = APP_DIR+os.sep+'Jalapeno'+os.sep+'source'+os.sep+'extension'


extension_file_mgr = Mgr(extension_path)

@app.context_processor
def extension_mgr():
	extensions_list = ext_content_list(extension_path)
	return dict(extensions = extensions_list)

@extension.route('/extension/<path:path>')
def ext(path):
	return send_from_directory(app.config['JS_EXTENSION_DIR'],
                               path, as_attachment=False)


def ext_content_list(path):
	extensions = extension_file_mgr.tree_dict()
	ext_content = []
	for k,v in extensions.items():
		ext_name= path+os.sep+v
		try:
			f = open(ext_name,'r')
			ext_content.append(Markup(f.read()))
			f.close()
		except:
			continue
	return ext_content
















app.register_blueprint(extension)