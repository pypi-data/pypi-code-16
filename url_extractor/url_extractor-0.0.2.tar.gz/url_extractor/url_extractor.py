#coding=utf-8

import re
from urlparse import urlparse
import urllib



urls = ["http://meiwen.me/src/index.html",
          "http://1000chi.com/game/index.html",
          "http://www.1000chi.com/game/index.html",
          "http://see.xidian.edu.cn/cpp/html/1429.html",
          "https://docs.python.org/2/howto/regex.html",
          """https://www.google.com.hk/search?client=aff-cs-360chromium&hs=TSj&q=url%E8%A7%A3%E6%9E%90%E5%9F%9F%E5%90%8Dre&oq=url%E8%A7%A3%E6%9E%90%E5%9F%9F%E5%90%8Dre&gs_l=serp.3...74418.86867.0.87673.28.25.2.0.0.0.541.2454.2-6j0j1j1.8.0....0...1c.1j4.53.serp..26.2.547.IuHTj4uoyHg""",
          "file:///D:/code/echarts-2.0.3/doc/example/tooltip.html",
          "http://api.mongodb.org/python/current/faq.html#is-pymongo-thread-safe",
          "https://pypi.python.org/pypi/publicsuffix/",
          "http://127.0.0.1:8000"
          ]


topHostPostfix = (
    '.com','.la','cn','.io','.co','.info','.net','.org','.me','.mobi',
    '.us','.biz','.xxx','.ca','.co.jp','.com.cn','.net.cn',
    '.org.cn','.mx','.tv','.ws','.ag','.com.ag','.net.ag',
    '.org.ag','.am','.asia','.at','.be','.com.br','.net.br',
    '.bz','.com.bz','.net.bz','.cc','.com.co','.net.co',
    '.nom.co','.de','.es','.com.es','.nom.es','.org.es',
    '.eu','.fm','.fr','.gs','.in','.co.in','.firm.in','.gen.in',
    '.ind.in','.net.in','.org.in','.it','.jobs','.jp','.ms',
    '.com.mx','.nl','.nu','.co.nz','.net.nz','.org.nz',
    '.se','.tc','.tk','.tw','.com.tw','.idv.tw','.org.tw',
    '.hk','.co.uk','.me.uk','.org.uk','.vg', ".com.hk")
regx = r'[^\.]+('+'|'.join([h.replace('.',r'\.') for h in topHostPostfix])+')$'
pattern = re.compile(regx,re.IGNORECASE)

class Domain_Extractor(object):

    def to_extract1(self,url):
        #no www
        parts = urlparse(url)
        host = parts.netloc
        m = pattern.search(host)
        res =  m.group() if m else host
        domain="unkonw" if not res else res
        return domain

    def to_extract2(self,url):
        proto, rest = urllib.splittype(url)
        res, rest = urllib.splithost(rest)
        domain= "unkonw" if not res else res
        return domain

def test():
    for url in urls:
        parts = urlparse(url)
        #print 'parts',parts
        host = parts.netloc

        m = pattern.search(host)
        res =  m.group() if m else host
        print "unkonw" if not res else res


    print "--"*40
    for url in urls:
        proto, rest = urllib.splittype(url)
        res, rest = urllib.splithost(rest)
        print "unkonw" if not res else res


