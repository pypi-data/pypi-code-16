if __name__ == '__main__':
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
		x = scraper.scrape(args[0],silent=True)
		t = Template(open(prefix + "template.html",'r').read())
		for p in range(len(x["data"])):
			x["data"][p][0] = ",".join(x["data"][p][0])
			x["data"][p][1] = x["data"][p][1]
		z = {}
		for a,b in x["data"]:
			z[a] = b
		with open('yourdata.html','wb') as w:
			xs = t.render(content=z,title=myTitle,time=str(datetime.datetime.now()),url=args[0],Stype=x["type"])
			w.write(xs.encode('utf-8'))
