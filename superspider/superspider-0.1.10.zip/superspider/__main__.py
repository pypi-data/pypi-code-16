if __name__ == '__main__':
	temp ="""
<html><head><title>{{title}}</title><style>.container{display:block;background:#cfd5e2;padding:5px;}.info{background:#afbacf;border-radius:5px;padding-left:6px;padding-right:6px;width:50%;margin:auto;font-weight:bold;}h1{text-align:center;font-family:Verdana;}pre{margin:0px;padding:0px;}table{border-collapse:separate; border-spacing:0; margin:2px; table-layout: fixed; width: 100%;}tr:nth-child(even){background-color: #9facc6;}tr:nth-child(odd){background-color: #dfe3ec; width: 25%;}th{font-family: Courier;font-size: 18px;}td{font-family: Verdana;font-size: 14px;padding:4px;word-wrap: break-word;overflow:auto;}td:nth-child(odd),th:first-child{width: 25%;}td:nth-child(even),th:nth-child(2){width: 75%;}td:nth-child(odd){border-right: 3px solid #435070;}body{background: #435070;}</style></head><body><div class="container"><h1>{{title}}</h1><div class="info"><pre>
Website: {{url}}
Identified Structure: {{Stype}}
Time Generated: {{time}}
				</pre></div></div><table><tbody><tr><th>Keywords</th><th>Text</th></tr>{% for keywords,text in content.items() %}<tr><td><p>{{keywords}}<p></td><td><p>{{text}}<p></td></tr>{% endfor %}</tbody></table></body></html>
"""
	from superspider import scraper
	import sys, datetime
	from jinja2 import Template
	args = sys.argv[1:]
	prefix = sys.argv[0].replace(__name__ + ".py","")
	if len(args) < 1:
		print("No website was specified.")
	else:
		myTitle = args[0].replace("https://","").replace("http://","")
		myTitle = myTitle[:myTitle.find("/")].split(".")[0] + "\'s Summary Data"
		myTitle = myTitle[0].upper() + myTitle[1:]
		x = scraper.scrape(args[0])
		t = Template(open(prefix + "template.html",'r').read())
		for p in range(len(x)):
			x[p][0] = ",".join(x[p][0])
			x[p][1] = x[p][1].text
		z = {}
		for a,b in x:
			z[a] = b
		with temp as w:
			w.write(t.render(content=z,title=myTitle,time=str(datetime.datetime.now()),url=args[0],Stype="Blog"))
