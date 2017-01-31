from geonode.settings import *
INSTALLED_APPS += ('geonode-client', "cartoview", "cartoview.app_manager", )
ROOT_URLCONF = "cartoview.urls"
import geonode
import cartoview
CARTOVIEW_ROOT = os.path.abspath(os.path.dirname(cartoview.__file__))
GEONODE_ROOT = os.path.abspath(os.path.dirname(geonode.__file__))
TEMPLATES[0]["DIRS"] = [os.path.join(CARTOVIEW_ROOT, "templates")] + TEMPLATES[0]["DIRS"]
STATICFILES_DIRS += [os.path.join(CARTOVIEW_ROOT, "static"),]
cartoview_apps_settings_path = os.path.join(CARTOVIEW_ROOT, 'app_manager', "settings.py")
execfile(cartoview_apps_settings_path)

LAYER_PREVIEW_LIBRARY = "react"