from flask import Blueprint, render_template
from Jalapeno.utils.flatpage import sitepages
from flask import request
from Jalapeno.utils.config import config
from Jalapeno.lib.selector import flatpage_filter,view_register,get_template




docs = Blueprint('docs',__name__)
L = config['views']['docs'].values()


def page(path):
	rule = request.url_rule.rule
	flat_rule = flatpage_filter(rule,config)
	titles = [[each.meta['title'],each.path] for each in sitepages[flat_rule]]
	article = sitepages[flat_rule].get_or_404(path)
	
	template = get_template(L,rule)
	
	return render_template(template,page=article,doctag=titles)

view_register(L,docs,page)