import os
import re
import crabmd as mistune
root = os.path.dirname(__file__)

known = []

styles = {
      "legal_italic":{
      "span":"i",
      "block":"legal_italic",
      "class":"g_legal_italic",
      "purpose":"Italics required to match prescribed formatting in legislation, documents or forms"},

      "legal_bold":{
      "span":"b",
      "block":"legal_bold",
      "class":"g_legal_bold",
      "purpose":"Bold required to match prescribed formatting in legislation, documents or forms"}
    }

def url_for(endpoint, **kwargs):
    url = '/url/' + endpoint
     
    if endpoint == "displaySnip":
        url += '/' + kwargs['type'] + '/' + kwargs['id']
        
        return url
        
    if endpoint == "displayArticle":
        url += '/' + kwargs['itemid']
        return url
        
    for x in kwargs.values(): 
        url += '/' + x
        
    return url
        
KM_STATIC = 'http://workspaces/P299KMProjectTeam/Guidance%20content/'    
m = mistune.Markdown(hn="hotdrop", url_for=url_for ,styles = styles, static = KM_STATIC)


def render(folder, name):
    filepath = os.path.join(folder, name + '.text')
    with open(filepath) as f:
        content = f.read()

    html = m.parse(content)

    filepath = os.path.join(folder, name + '.html')
    with open(filepath) as f:
        result = f.read()

    html = re.sub(r'\s', '', html)
    result = re.sub(r'\s', '', result)
    for i, s in enumerate(html):
        if s != result[i]:
            begin = max(i - 30, 0)
            msg = '\n\n%s\n------Not Equal(%d)------\n%s' % (
                html[begin:i+30], i, result[begin:i+30]
            )
            raise ValueError(msg)
    assert html == result


def listdir(folder):
    folder = os.path.join(root, 'crabmd_fixtures', folder)
    files = os.listdir(folder)
    files = filter(lambda o: o.endswith('.text'), files)
    names = map(lambda o: o[:-5], files)
    return folder, names


def test_crab():
    folder, names = listdir('crabmd')
    for key in names:
        yield render, folder, key
