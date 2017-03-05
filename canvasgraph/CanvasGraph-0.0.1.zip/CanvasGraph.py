#encoding: utf-8
from wsgiref.simple_server import make_server
from cgi import parse_qs, escape
from os.path import dirname
import json

def fn(s,c):
    KB=json.loads(s)
    ksel=set()
    for k in KB:
        if KB[k]['s']==1:
            ksel.add(k)
            KB[k]['s']=0
    for k in KB:
        if k in ksel:
            if c==1:
                KB[k]['n']=list( set(KB[k]['n']) | (ksel - set([k])) )
            else:
                KB[k]['n']=list( set(KB[k]['n']) - (ksel - set([k])) )
    save(KB)
    return json.dumps(KB)

def save(KB):
    f=open(cd+"\\KB.js",'w')
    f.write("var KB=%s"%json.dumps(KB))
    f.close()

def application(environ, start_response):
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0
    request_body = environ['wsgi.input'].read(request_body_size)
    #print request_body
    parameters = parse_qs(request_body)
    #print parameters  
    if 'KB' in parameters:
        KB=escape(parameters['KB'][0])
        c=escape(parameters['c'][0])
        response_body=fn(KB,int(c))
    else:
        response_body=html
    if environ.get("PATH_INFO", "")=="/KB.js":
        response_body=js
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [response_body]


#KB={"1":{"x":10,"y":10,"s":0,"n":["2"]}, "2":{"x":60,"y":60,"s":0,"n":[]}, "3":{"x":60,"y":20,"s":0,"n":[]}, "4":{"x":80,"y":80,"s":0,"n":[]} }
#save(KB)
cd=dirname(__file__) 
html=open(cd+"\\canvas.html",'r').read()
js=open(cd+"\\KB.js",'r').read()
import webbrowser
webbrowser.open("http://localhost:80")
httpd = make_server('localhost', 80, application)
httpd.serve_forever()