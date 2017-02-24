import urllib
import urllib.request
import webbrowser
import urllib.request as urlRequest

source_url = "http://sh.st/st/d6c5a0ef286df8b3a1af5c9e65b29c2f/http://toonvideoindia.blogspot.com/2016/07/samurai-jack-episode-i-beginning.html"
#print source_url

def print_all(_list):
    for each  in _list:
        print (each)
        #print ("\n")

# renders a web page
def get_page(url):
    # pretend to be a chrome 47 browser on a windows 10 machine
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"}
    req = urlRequest.Request(url, headers = headers)
    # open the url
    x = urlRequest.urlopen(req)
    # get the source code
    sourceCode = x.read().decode('utf8')
    return sourceCode
#3
def parent_link(url):
    page = get_page(url)
    link = get_all_links(page)
    return link
#2
def get_all_links(page):
    links = []
    while True:
        url,endpos = get_next_target(page)
        if url:
            links.append(url)
            page = page[endpos:]
        else:
            break
    return links
#1
def get_next_target(page):
    start_link = page.find('http://toon')
    if start_link == -1: 
        return None, 0
    start_quote = page.find("http", start_link - 11)
    end_quote = page.find('"', start_quote + 1)
    url = page[start_quote:end_quote]
    return url, end_quote

#4
def get_target(url):
    page = get_page(url)
    start_link = page.find('https://drive.google.com')
    if start_link == -1:
        return None
    start_quote = page.find("http", start_link - 24)
    end_quote = page.find('"', start_quote + 1)
    url = page[start_quote:end_quote]
    return url
#5
def get_all_childs(_list):
    links = []
    for each in _list:
        foo = get_target(each)
        if foo not in links:
            links.append(foo)
        else:
            break
    return links

# opens a link in browser
def open_page(url):
    return webbrowser.open(url)

# 6
def give_me(url):
    links = parent_link(url)
    child_links = get_all_childs(links)
    return child_links

#7
def extract_id(link):
    start_id = link.find("/file/d/")
    if start_id == -1:
        return None
    start = link.find("/", start_id + 7)
    end = link.find("/", start + 1)
    link_id = link[start + 1:end]
    return link_id

#8
def extract_all_id(links):
	all_id = []
	for each in links:
		foo = extract_id(each)
		if foo not in links:
			all_id.append(foo)
		else:
			break
	return all_id

#9
def link(link_id):
	link = "https://drive.google.com/uc?id=" + link_id + "&export=download"
	return link

#10
def download_link(drive_id):
	ids = []
	for each in drive_id:
		foo = link(each)
		if foo not in ids:
			ids.append(foo)
	return ids

#
def final(parent_url):
    foo = give_me(parent_url)
    ids = extract_all_id(foo)
    final_links = download_link(ids)
    for each in final_links:
        open_page(each)
    return final_links
