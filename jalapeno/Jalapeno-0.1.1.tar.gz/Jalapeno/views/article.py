from flask import Blueprint, render_template,request
from Jalapeno.utils.flatpage import sitepages
from Jalapeno.utils.configuration import config
from Jalapeno.lib.selector import flatpage_filter,view_register,get_template

try:
	L = config['views']['article'].values()
except:
	exit()

article = Blueprint('article',__name__)

def page(path):
	rule = request.url_rule.rule
	flat_rule = flatpage_filter(rule,config)
	
	template = get_template(L,rule)


	article = sitepages[flat_rule].get_or_404(path)
	return render_template(template,page=article)





view_register(L,article,page)