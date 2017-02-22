from flask import Blueprint, render_template,request
from Jalapeno.utils.config import config
from Jalapeno.lib.selector import view_register,get_template

page = Blueprint('page',__name__)

try:
	L = config['views']['page'].values()

except:
	exit()

def webpage():
	rule = request.url_rule.rule

	template = get_template(L,rule)

	return render_template(template)





		
view_register(L,page,webpage)