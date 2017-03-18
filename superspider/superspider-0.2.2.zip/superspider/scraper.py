import urllib.request as req
import sys, nltk, string, json, datetime
from bs4 import BeautifulSoup as bsoup
from nltk.corpus import brown
# blogs are more opiniontated, while another website is more about a certain product.
# A gateway is none.
#
#
### our specific functions for each webpage structure
#
#
def getBlogSections(tree,silent=False):
	"""Gets the sections of a blog."""
	# import here, since not all structures use this feature
	from nltk import word_tokenize
	x = ffilter(tree)
	if len(x) > 1:
		if not silent:
			print("Warning! Found more than one content window!")
	if len(x) == 0:
		if not silent:
			print("Error! No main content window found")
	else:
		if not silent:
			print("Attempting to find sections of text...")
		sectionList = []
		for i in x:
			sectionList.extend(util.getSections(i))
		if not silent:
			print("Stripping json from text found...")
		for i in range(len(sectionList)):
			try:
				json.loads(sectionList[i][1].text)
				if sectionList[i][1].text.strip(string.punctuation) == "":
					print("DUDE")
					raise Exception
			except:
				pass
			else:
				sectionList.pop(i)
				if not silent:
					print("Popped %s" % i)
	for i in range(len(sectionList)):
		sectionList[i] = [[],sectionList[i][1].text]
	# before doing some filtering of the headers, load in our word index
	tIndex = util.data.brown_words
	if not silent:
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
			if not silent:
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
	return (good_headers,sectionList)
def getGatewaySections(tree):
	raise Exception("FEATURE NOT IMPLIMENTED.")
def printUnscrapable(tree):
	raise Exception("Web page portrays no signifying features, and is too small to scrape.")
def getCompanySections(tree):
	raise Exception("FEATURE NOT IMPLIMENTED.")
def getMiniSections(tree,silent=False):
	"""Attempts to find something that is being described by a small, intricate website."""
	# import here, since not all structures use this feature
	from nltk.corpus import stopwords
	from nltk import word_tokenize
	# eventually, these will make up our keywords
	t = tree.text.replace(tree.head.text,"").replace("\n","").replace("		","").replace("   ","").lower()
	t = t.strip(string.punctuation)
	stop = set(stopwords.words("english"))
	t = word_tokenize(t)
	t = [w for w in t if not w in stop]
	count = {}
	for i in t:
		try:
			if util.data.brown_words[i] == "NNP":
				if i in count:
					count[i]+=1
				else:
					count[i]=1
		except KeyError:
			if i in count:
				count[i]+=1
			else:
				count[i]=1
	count = [(k,count[k]) for k in count]
	count = sorted(count,reverse=True,key=lambda tup: tup[1])[:5]
	# grab the top 5 words.
	keywords = [x[0] for x in count]
	# onto the sections
	sections = tree.findAll("p")
	sectionList = []
	for section in sections:
		for i in keywords:
			if "".join(section.text).lower().find(i.lower()) >= 0:
				sectionList.append([[],section.text])
				break
	return (keywords,sectionList)
#
#
### Useful fundamental properties and methods. Not user friendly
#
#
class util:
	"""Useful fundamental properties and methods."""
	structures = {
		"blog" : getBlogSections,
		"gateway" : getGatewaySections,
		"unscrapeable" : printUnscrapable,
		"company_home" : getCompanySections,
		"mini" : getMiniSections
	}
	class data:
		content_words = ["main","content","body"]
		tags = ["<!DOCTYPE>","<a>","<abbr>","<acronym>","<address>","<applet>","<area>","<article>","<aside>","<audio>","<b>","<base>","<basefont>","<bdi>","<bdo>","<big>","<blockquote>","<body>","<br>","<button>","<canvas>","<caption>","<center>","<cite>","<code>","<col>","<colgroup>","<datalist>","<dd>","<del>","<details>","<dfn>","<dialog>","<dir>","<div>","<dl>","<dt>","<em>","<embed>","<fieldset>","<figcaption>","<figure>","<font>","<footer>","<form>","<frame>","<frameset>","<h1>","<h2>","<h3>","<h4>","<h5>","<h6>","<head>","<header>","<hr>","<html>","<i>","<iframe>","<img>","<input>","<ins>","<kbd>","<keygen>","<label>","<legend>","<li>","<link>","<main>","<map>","<mark>","<menu>","<menuitem>","<meta>","<meter>","<nav>","<noframes>","<noscript>","<object>","<ol>","<optgroup>","<option>","<output>","<p>","<param>","<picture>","<pre>","<progress>","<q>","<rp>","<rt>","<ruby>","<s>","<samp>","<script>","<section>","<select>","<small>","<source>","<span>","<strike>","<strong>","<style>","<sub>","<summary>","<sup>","<table>","<tbody>","<td>","<textarea>","<tfoot>","<th>","<thead>","<time>","<title>","<tr>","<track>","<tt>","<u>","<ul>","<var>","<video>","<wbr>"]
		brown_words = dict(brown.tagged_words())
	def grabSite(url):
		"""Returns a website, already parsed by bs4's BeautifulSoup."""
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
#
#
### Functions that are more specialized to the purpose of this program. Not user friendly
#
#
def rank_tags(tree,silent=False):
	"""Goes through all possible html5 tags, and then spits out a list greatest to least. The tuple is as follows: (tag_name,tag_count)."""
	tags = []
	excludes = ["body","head","!DOCTYPE","title","style","span","html"]
	myTags = util.data.tags
	for i in excludes:
		try:
			myTags.remove("<" + i + ">")
		except:
			if not silent:
				print("Intereseting... %s is not in the document." % ("<" + i + ">"))
	def doStrip(x):return x.strip("<>!")
	myTags = list(map(doStrip,myTags))
	for i in myTags:
		x = len(tree.findAll(i))
		if x > 0:
			tags.append((i,x))
	tags = sorted(tags,reverse=True,key=lambda tup: tup[1])
	return tags
def ffilter(tree,structure="high"):
	"""Trys to find a "main content" node in the webpage."""
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
def getHeaders(tree,silent=False):
	"""Trys to find the number of headers on the page, out of all the tags that could represent one."""
	ranking = rank_tags(tree,silent=silent)
	headCount = 0
	headerTCount = None
	for tag,count in ranking:
		if tag[0] == "h" and len(tag) == 2:
			headCount+=count
		if tag == "header":
			headerTCount = count
	if headerTCount != None:
		if headerTCount < headCount:
			headCount = headerTCount
	return headCount
#
#
### The actually algorithmic part of this script.
#
#
def getSiteType(tree,silent=False):
	"""Where the magic happens. Probably the most "algorithm-like" part of the program."""
	### constants
	#
	#
	LINK_TO_PARAGRAPH_MAX_QUOTIENT = 4
	COMPANY_IMAGE_TO_PARACOUNT_MIN_QUOTIENT = 3
	COMPANY_HEAD_TO_PARA_MIN_QUOTIENT = 2
	COMPANY_MIN_HEAD = 6
	MIN_TEXT = 4000
	MIN_GATEWAY_WINDOWS = 6
	#
	#
	### code
	#
	#
	# variables we'll use in determining the structure
	mainWindow = ffilter(tree)
	#
	### First, see if it's a blog. (This is the easiest structure of website to scrape and identify.)
	#
	imgCount = len(tree.findAll("img"))
	paraCount = len(tree.findAll("p"))
	headCount = getHeaders(tree,silent=silent)
	if imgCount / paraCount > COMPANY_IMAGE_TO_PARACOUNT_MIN_QUOTIENT or headCount / paraCount >= COMPANY_HEAD_TO_PARA_MIN_QUOTIENT and headCount >= COMPANY_MIN_HEAD:
		return "company_home"
	elif len(mainWindow) > 0:
		if len(mainWindow) > MIN_GATEWAY_WINDOWS:
			return "gateway"
		else:
			mainWindow = mainWindow[0]
			ranking = rank_tags(mainWindow,silent=silent)
			rankIndex = dict(ranking)
			headers = getHeaders(tree,silent=silent)
			if "p" in rankIndex and headers > 0:
				if "a" in rankIndex:
					# The 4 is just a random constant
					if rankIndex["a"] / rankIndex["p"] <= LINK_TO_PARAGRAPH_MAX_QUOTIENT:
						return "blog"
					else:
						return "gateway"
	else:
		# could still be a gateway
		ranking = rank_tags(tree,silent=silent)
		rankIndex = dict(ranking)
		headers = getHeaders(tree,silent=silent)
		if "p" in rankIndex and headers > 0:
			if "a" in rankIndex:
				# The 4 is just a random constant
				if rankIndex["a"] / rankIndex["p"] > LINK_TO_PARAGRAPH_MAX_QUOTIENT:
					return "gateway"
				elif "img" in rankIndex:
					if rankIndex["a"] / rankIndex["p"] > LINK_TO_PARAGRAPH_MAX_QUOTIENT / 2 and rankIndex["a"] / rankIndex["img"] >= COMPANY_IMAGE_TO_PARACOUNT_MIN_QUOTIENT:
						return "gateway"
		# seeing if this is pointless
		bad = "#$%&\"\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c"
		textt = tree.text.replace(tree.head.text,"").strip(bad).replace("\n","").replace("	","").replace(" ","")
		for i in bad:
			textt = textt.replace(i,"")
		if len(tree.text.strip()) < MIN_TEXT:
			return "unscrapeable"
		else:
			return "mini"
#
#
### User friendly functions.
#
#
def scrape(url,silent=False):
	"""Really the "main()" function of the program."""
	if not silent:
		print("GETting [%s]..." % url)
	# global for debugging
	global x
	x = util.grabSite(url)
	if not silent:
		print("filtering tags in html tree...")
	Stype = getSiteType(x,silent=silent)
	sectionList = None
	if Stype in util.structures:
		if not silent:
			print("IDENTIFIED %s" % Stype)
		good_headers,sectionList = util.structures[Stype](x,silent=silent)
		if sectionList != None:
			# remove duplicates from headers
			good_headers = set(good_headers)
			# add headers onto sections, if it is appropriate.
			for title in good_headers:
				for p2,i in enumerate(sectionList):
					if title.lower() in str(i[1]).lower():
						sectionList[p2][0].append(title)
			output = {
				"data" : sectionList,
				"time" : str(datetime.datetime.now()),
				"type" : Stype
			}
			return output
	else:
		##raise Exception("Could not identify website structure type.")
		if not silent:
			print("I AINT GOT NO TYPE")
