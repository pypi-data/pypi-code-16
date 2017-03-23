# encoding: utf-8
from gopage import util
from gopage import parser
import random
import requests


class Proxy:
    PROXIES = []

    @classmethod
    def add_proxies(cls):
        url = 'http://erwx.daili666.com/ip/?tid=558045424788230&num=20&foreign=only'
        proxies = requests.get(url).text.splitlines()
        cls.PROXIES = [p.strip() for p in proxies]

    @classmethod
    def pop_proxy(cls, proxy_ip):
        if cls.PROXIES and proxy_ip in cls.PROXIES:
            cls.PROXIES.remove(proxy_ip)

    @classmethod
    def choose_proxy(cls):
        if not cls.PROXIES:
            cls.add_proxies()
        return random.choice(cls.PROXIES)


def download_page(url, useproxy=True, verbose=True, maxtry=2, timeout=5):

    def retry():
        if verbose:
            print('[FAIL-{}] {} -> {}'.format(maxtry, proxy_ip, url))
        return download_page(url, useproxy, verbose, maxtry - 1, timeout)

    if maxtry <= 0:
        return None
    try:
        proxy_ip = 'localhost'
        if useproxy:
            proxy_ip = Proxy.choose_proxy()
        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1 WOW64 rv:23.0) Gecko/20130406 Firefox/23.0'
        }
        proxy = {
            'http': proxy_ip
        }
        content = requests.get(url, proxies=proxy, headers=header).text

        if verbose:
            print('[OK] {} -> {}'.format(proxy_ip, url))
        return content

    except Exception as e:
        if useproxy:
            Proxy.pop_proxy(proxy_ip)
        return retry()


@util.cache('text')
def search(query, useproxy=True, verbose=True, maxtry=5, timeout=5, checkpage=True):
    query = query.replace(' ', '+')
    url = 'https://www.google.com/search?hl=en&safe=off&q={}'.format(query)
    page = download_page(url, useproxy, verbose, maxtry, timeout)
    if checkpage:
        snippets = parser.parse(page)
        if not snippets:
            return None
    return page


if __name__ == '__main__':
    names = [
        'jie tang',
        'jiawei han',
        'thorsten joachims'
    ]
    for name in names:
        with open('{}.html'.format(name), 'w', encoding='utf-8') as wf:
            page = search(name, usecache=True,
                          cache='{}.html'.format(name.replace(' ', '')))
            wf.write(page)
            # page = requests.get('http://baidu.com')
