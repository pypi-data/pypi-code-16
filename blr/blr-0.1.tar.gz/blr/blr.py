import requests
import sys
import time
from bs4 import BeautifulSoup
from prettytable import PrettyTable

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def search():
    print("Loading...")
    start = time.time()
    html = requests.get('http://bolor-toli.com/dictionary/word?search', params = {'search': sys.argv[1]}).text
    soup = BeautifulSoup(html,"html.parser")
    table = soup.find(id="search_result_table")
    t = PrettyTable(['EN', 'MN'])
    for tr in table.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) > 7:
            mn = bcolors.WARNING + tds[6].a.string + bcolors.ENDC
            t.add_row([tds[3].strong.string, mn.encode('utf-8')])
    print(t)
    print("time " + str(time.time() - start) + "sec" )


if len(sys.argv) > 1:
    search()
else:
    print "Please enter search word"
    




    
