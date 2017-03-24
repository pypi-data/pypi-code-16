from flask import Blueprint, render_template,request
from Jalapeno.utils.flatpage import sitepages
from Jalapeno.utils.config import config
from Jalapeno.lib import pagination as Pag
from Jalapeno.lib.selector import flatpage_filter,view_register,get_template


posts = Blueprint('posts',__name__)



try:
	L = config['views']['posts'].values()
except:
	exit()

def postpage(page=1):

	rule = request.url_rule.rule
	flat_rule = flatpage_filter(rule,config)
	posts = [article for article in sitepages[flat_rule] if 'date' in article.meta]

	PER_PAGE = 6
	   
	template = get_template(L,rule)

	
	sorted_posts = sorted(posts,reverse = True,key = lambda page:page.meta['date'])

	if config['Pagination']:
		pager_obj = Pag.Pagination(page,PER_PAGE,sorted_posts)
	return render_template(template,pagination = pager_obj)



view_register(L,posts,postpage)