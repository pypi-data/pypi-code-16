from flask import Blueprint, render_template,request
from Jalapeno.utils.flatpage import sitepages
from Jalapeno.utils.config import config
from Jalapeno.lib.selector import flatpage_filter,view_register,get_template

try:
	L = config['views']['markpage'].values()
except:
	exit()

markpage = Blueprint('markpage',__name__)

def marker(path):
	rule = request.url_rule.rule
	
	
	template = get_template(L,rule)


	markpage = sitepages['markpage'].get_or_404(path)
	return render_template(template,page=markpage)





view_register(L,markpage,marker)