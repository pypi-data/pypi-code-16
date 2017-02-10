import sys
import requests
from bs4 import BeautifulSoup


def search_naver_dic(query_keyword):
    dic_url = """http://endic.naver.com/search.nhn?sLn=kr&dicQuery={0}&x=12&y=12&query={0}&target=endic&ie=utf8&query_utf=&isOnlyViewEE=N
Method=GET"""
    r = requests.get(dic_url.format(query_keyword))
    soup = BeautifulSoup(r.text, "html.parser")
    result_means = soup.find_all(attrs={'class':'fnt_k05'})
    print_result("naver", result_means)


def search_daum_dic(query_keyword):
    dic_url = """http://dic.daum.net/search.do?q={0}"""
    r = requests.get(dic_url.format(query_keyword))
    soup = BeautifulSoup(r.text, "html.parser")
    result_means = soup.find_all(attrs={'class':'list_search'})
    print_result("daum", result_means)


def print_result(site, result_means):
    print "*" * 25
    print "*** %s dic ***" % site
    print "*" * 25
    for elem in result_means:
        text = elem.get_text().strip()
        if text:
            print text.replace('\n', ', ')
    print


def main(args=None):
    """The main routine."""
    if len(sys.argv) < 2:
        print "Usage : kdic [keyword]"
        sys.exit(0)

    query = sys.argv[1]
    search_naver_dic(query)
    search_daum_dic(query)


if __name__ == "__main__":
    main()