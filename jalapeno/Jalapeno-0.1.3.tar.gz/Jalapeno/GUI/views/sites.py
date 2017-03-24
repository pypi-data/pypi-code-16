from flask import Blueprint,render_template,request
from Jalapeno.lib.siteMgr import Site
sites = Blueprint('sites',__name__)








@sites.route('/sites')
def show():
	return render_template('sites.html')


@sites.route("/sites/site-create",methods =['GET','POST'])
def create():
	try:
		sitename = request.get_data().decode()
		Site.site_create(sitename)
		Site.site_list_add(sitename)
	except:
		print('Something wrong when creating')
		pass
	return render_template('sites.html')

@sites.route("/sites/switch-site",methods =['GET','POST'])
def switch():
	try:
		sitename = request.get_data().decode()
		if Site.site_switch(sitename):
			return sitename
		else:
			return None
	except:
		pass

@sites.route("/sites/current-site",methods =['GET','POST'])
def current():
	try:
		sitename = Site.get_site()
	except:
		pass
	return sitename