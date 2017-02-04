from Jalapeno.lib.jalop_markdown import Jalop_markdown
from Jalapeno import app
from Jalapeno.utils.flatpage import sitepages
from flask import request
from Jalapeno.utils.configuration import config
from Jalapeno.lib.selector import flatpage_filter


@app.template_filter('excerpt')
def excerpt_spliter(article):
    rule = request.url_rule.rule
    flat_rule = flatpage_filter(rule,config)
    content = Jalop_markdown(article,sitepages[flat_rule])
    
    sidesep = '<!--Sidebar-->'

    if sidesep in content:
        content = content.split(sidesep,1)[1]

    sep='<!--More-->'
    return content.split(sep,1)[0] if sep in content else ''


@app.template_filter('content')
def content_spliter(article):
    rule = request.url_rule.rule
    flat_rule = flatpage_filter(rule,config)
    content = Jalop_markdown(article,sitepages[flat_rule])
    sep='<!--Sidebar-->'
    return content.split(sep,1)[1] if sep in content else content


@app.template_filter('sidebar')
def content_spliter(article):
    rule = request.url_rule.rule
    flat_rule = flatpage_filter(rule,config)
    content = Jalop_markdown(article,sitepages[flat_rule])
    sep='<!--Sidebar-->'
    return content.split(sep,1)[0] if sep in content else ''




		
	























