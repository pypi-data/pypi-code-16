from Jalapeno.core import app


@app.template_filter('excerpt')
def excerpt_spliter(article):
    sidesep = '<!--Sidebar-->'
    if sidesep in article:
        article = article.split(sidesep,1)[1]

    sep='<!--More-->'
    return article.split(sep,1)[0] if sep in article else ''

@app.template_filter('content')
def content_spliter(article):

    sep='<!--Sidebar-->'
    return article.split(sep,1)[1] if sep in article else article


@app.template_filter('sidebar')
def content_spliter(article):
    sep='<!--Sidebar-->'
    return article.split(sep,1)[0] if sep in article else ''	
	























