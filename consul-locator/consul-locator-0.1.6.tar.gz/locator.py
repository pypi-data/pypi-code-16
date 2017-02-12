import threading
import consul
import requests
import time
import logging
import json
from os import environ
from urlparse import urlparse

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('consul')
logger.setLevel(
    logging.DEBUG if environ.get(
        'CONSUL_LOCATOR',
        'INFO') == 'DEBUG' else logging.INFO)


class Locator:
    c = None
    services = {}

    method_map = dict(
        get=requests.get,
        post=requests.post,
        put=requests.put,
        delete=requests.delete)

    def use(self, **kwargs):
        Locator.c = consul.Consul(**kwargs)

    def request(self, method, url, **kwargs):
        o = urlparse(url)
        if o.scheme == 'http' or o.scheme == 'https':
            return Locator.method_map.get(method, requests.get)(url, **kwargs)
        else:
            service_url = self.url_for(o) if Locator.c is not None else \
                url.replace('service://', 'http://')
            logger.debug(service_url)
            return Locator.method_map.get(
                method, requests.get)(
                service_url, **kwargs)

    def url_for(self, o):
        if o.scheme == 'service':
            if Locator.services.get(o.netloc, None):
                index = Locator.services.get(o.netloc, {}).get('index', 0)
                data = Locator.services.get(o.netloc, {}).get('data', [])
                index = (index + 1) % len(data)
                Locator.services[o.netloc]['index'] = index
                return 'http://' + data[index]['Service']['Address'] + \
                    ':' + str(data[index]['Service']['Port']) + \
                    o.path + '?' + o.query
            else:
                self.discover(o.netloc)
                time.sleep(1)
                return self.url_for(o)
        else:
            raise Exception('Unknow stream')

    def discover(self, service):
        def loop_discover():
            index = None
            while True:
                index, data = Locator.c.health.service(
                    service, index=index, passing=True)
                logger.debug(
                    "Service " +
                    service +
                    ' has been updated: ' +
                    json.dumps(
                        data,
                        indent=2))
                Locator.services[service] = dict(index=0, data=data)
        t = threading.Thread(target=loop_discover)
        t.daemon = True
        t.start()

    def get(self, url, **kwargs):
        return self.request('get', url, **kwargs)

    def post(self, url, **kwargs):
        return self.request('post', url, **kwargs)

    def put(self, url, **kwargs):
        return self.request('put', url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request('delete', url, **kwargs)


http = Locator()

if __name__ == "__main__":

    l = Locator()
    # l.use(host='10.60.3.231')
    logger.info(http.get('service://inbox/health'))
