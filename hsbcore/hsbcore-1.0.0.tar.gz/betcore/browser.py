#-*- coding:utf-8 -*-
import logging,socket
import Queue,threading
import requests
from time import sleep
from _ssl import SSLError as InnerSSLError
from requests.cookies import cookiejar_from_dict
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from requests.exceptions import Timeout, TooManyRedirects, SSLError, ConnectionError
from betcore.util import timimng_func
from betcore.exception import DownlineExcpetion,SysMaintenanceExcpetion

logger = logging.getLogger(__name__)
#import httplib
#httplib.HTTPConnection.debuglevel = 1
class SourceAddressAdapter(HTTPAdapter):
    def __init__(self, source_address, **kwargs):
        self.source_address =(source_address,0)
        super(SourceAddressAdapter, self).__init__(**kwargs)
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections, maxsize=maxsize, block=block, source_address=self.source_address)

common_headers={ 'User-Agent': 'Mozilla/5.1 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'q=0.8,en-us;q=0.5,en;q=0.3', 'Accept-Encoding': 'gzip, deflate', 'DNT':'1' }
class BaseBrowser(object):

    def __init__(self,site,lang='en_US',source_ip=None,cookies={}):
        self.site,self.lang,self.session=site,lang,requests.Session()
        if source_ip:
            self.session.mount('http://', SourceAddressAdapter(source_ip))
            self.session.mount('https://', SourceAddressAdapter(source_ip))
        self.session.headers.update(common_headers)
        self.session.cookies=cookiejar_from_dict(cookies)

    def get_res(self,url,data=None,retry=3,timeout=3):
        while 1:
            try:
                if data:
                    return self.session.post(url,data,timeout=timeout)
                else:
                    return self.session.get(url,timeout=timeout)
            except (Timeout,ConnectionError,socket.timeout,SSLError,InnerSSLError):
                if retry<=0:
                    return None
                else:
                    logger.exception("请求超时，重试。。。睡眠3秒")
                    sleep(0.5); retry-=1
            except TooManyRedirects:
                raise DownlineExcpetion(self)

    def get_res_content(self,url,data=None,retry=3,timeout=3):
        res=self.get_res(url, data, retry,timeout)
        return "" if res is None else res.content

    def get_res_by_json(self,url,data=None,retry=3,timeout=3):
        try :
            res =self.get_res(url, data, retry,timeout)
            return res.json()
        except ValueError:
            logger.info("掉线了？？？%s" %url)
            rt=res.content
            logger.info(rt)
            if rt.find("Maintenance")>0: raise SysMaintenanceExcpetion()
            raise DownlineExcpetion(self)

    def clean_cookies(self):
        pass

    def fetch_and_process(self,url,processor,queue):
        content=timimng_func("用户%s完成抓数长城的数据" %self.account[0],self.get_res_content,url)
        queue.put(processor(content))

    def fetch_and_process_parallel(self,urls,processors):
        result = Queue.Queue()
        threads = []
        for idx,url in enumerate(urls):
            threads.append(threading.Thread(target=self.fetch_and_process, args = (url,processors[idx],result)))
        for t in threads:t.start()
        for t in threads:t.join()
        while not result.empty():
            rs=result.get()
            if rs==-1:
                raise DownlineExcpetion(self)
            elif rs==0:
                return 0
        return 1

    def clean_cookies_domain(self):
        cookies={k:v for k,v in self.session.cookies.items()}
        self.session.cookies=cookiejar_from_dict(cookies)

    def __getitem__(self, key):
        return self.__dict__[key]

if __name__ == '__main__':
    pass
