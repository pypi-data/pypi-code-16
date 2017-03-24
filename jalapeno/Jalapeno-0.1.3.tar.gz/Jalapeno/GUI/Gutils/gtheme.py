
from Jalapeno.GUI.G import gui
from Jalapeno.lib import themeMgr




gui_theme = theme = themeMgr.Theme('GUI')


@gui.context_processor
def gui_theme_processor():
	
	gui_assets = gui_theme.static_url_for()
	return dict(gui=gui_assets)
