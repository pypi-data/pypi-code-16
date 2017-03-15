from bs4 import BeautifulSoup as bsoup
import urllib.request as req
import sys, nltk, string, json
from nltk import word_tokenize
from nltk.corpus import brown
class util:
	class data:
		content_words = ["main","content","body"]
def grabSite(url):
	try:
		r = req.urlopen(url)
	except:
		raise Exception("unable to GET website [%s]." % (url))
	else:
		try:
			t = bsoup(r.read(),'html.parser')
		except:
			raise Exception("Unable to parse website using BeautifulSoup.")
		else:
			return t
def ffilter(tree,structure="high"):
	good_divs = []
	Ttags = ["div","section"]
	for tag in Ttags:
		for i in util.data.content_words:
			for j in ["id","class"]:
				good_divs.extend(tree.findAll(tag,{j : i}))
	pops = []
	for p,i in enumerate(good_divs):
		arr = [[p2,z] for p2,z in enumerate(good_divs)]
		arr.pop(p)
		for j in arr:
			# remove duplicates. We just want the larger parent node/tag
			if str(i) in str(j):
				pops.append(j[0])
	for pop in pops:
		good_divs.pop(pop)

	return good_divs
def getSections(node):
	def divSpider(div):
		total = []
		currentHeader = []
		for n in div.children:
			if n.name:
				if n.name == "div":
					s = divSpider(n)
					total.extend(s)
				elif n.name[0] == "h" and len(n) == 2:
					currentHeader = [n.text]
				elif n.text.strip() != "":
					if [].extend(currentHeader):
						total.append([[].extend(currentHeader),n])
					else:
						total.append([[],n])
					currentHeader = []
		return total
	# note: node should be a div
	return divSpider(node)
def scrape(url):
	print("GETting [%s]..." % url)
	# global for debugging
	global x
	x = grabSite(url)
	print("filtering tags in html tree...")
	x = ffilter(x)
	if len(x) > 1:
		print("Warning! Found more than one content window!")
	if len(x) == 0:
		print("Error! No main content window found")
	else:
		print("Attempting to find sections of text...")
		sectionList = []
		for i in x:
			sectionList.extend(getSections(i))
		print("Stripping json from text found...")
		for i in range(len(sectionList)):
			try:
				json.loads(sectionList[i][1].text)
			except:
				pass
			else:
				sectionList.pop(i)
				print("Popped %s" % i)
		# before doing some filtering of the headers, load in our word index
		print("Loading \"brown\" word index...")
		tIndex = dict(brown.tagged_words())
		print("Associating arbitrary headers with paragraphs...")
		# add on headers if they are missing.
		headers = []
		good_headers = []
		for z in x:
			for i in range(1,7):
				headers.extend([j.text for j in z.findAll("h%s" % i)])
		for i in headers:
			tx = i.strip(string.punctuation.strip("$@#&%")).split(" ")
			try:
				tx = nltk.pos_tag(tx)
			except:
				print("Hit Error using nltk on a header. Skipping")
				continue
			for i in tx:
				if i[1] == "NNP" and i[0].strip(string.punctuation) != "":
					try:
						tIndex[i[0]]
					except KeyError:
						good_headers.append(i[0])
					else:
						if tIndex[i[0]].find("NN") >= 0 :
							good_headers.append(i[0])
		# remove duplicates from headers
		good_headers = set(good_headers)
		# add headers onto sections, if it is appropriate.
		for title in good_headers:
			for p2,i in enumerate(sectionList):
				if title.lower() in i[1].text.lower():
					sectionList[p2][0].append(title)
		##print(sectionList)
		return sectionList