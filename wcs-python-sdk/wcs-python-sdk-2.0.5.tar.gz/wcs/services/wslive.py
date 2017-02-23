from wcs.commons.auth import Auth
from wcs.commons.config import MGR_URL
from wcs.commons.config import logging_folder
from wcs.commons.http import _get
from wcs.commons.util import get_logger

class WsLive(object):

    def __init__(self, auth):
        self.auth = auth
        self.mgr_host = MGR_URL
        self.logger = get_logger(logging_folder, 'WsLive')

    def gernerate_headers(self,url,body=None):
        token = self.auth.managertoken(url,body=body)
        headers = {'Authorization': token}
        return headers

    def params_parse(self, params):
        if params:
            paramlist = []
            for k, v in params.items():
                paramlist.append('{0}={1}'.format(k, v))
            paramlist = '&'.join(paramlist)
        return paramlist
   
    def make_list_url(self, param):
        url = ['{0}/wslive/list'.format(self.mgr_host)] 
        if param:
            url.append(self.params_parse(param))
        url = '?'.join(url)
        return url

    def wslive_list(self, channelname, startTime, endTime, bucket, start=None, limit=None):
        query = {
            'channelname' : channelname,
            'startTime' : startTime,
            'endTime' : endTime,
            'bucket' : bucket,
        }
        if start is not None:
            query['start'] = start
        if limit is not None:
            query['limit'] = limit
        url = self.make_list_url(query)
        if query is not None:
            self.logger.info('List params is %s', query)
        self.logger.info('List bucket %s', bucket)
        print("wslive_list:"+url)
        print("\n")
        print(query)
        print("\n")
        print(self.gernerate_headers(url))
        print("\n")
        code, text = _get(url=url, data=query, headers=self.gernerate_headers(url)) 
        self.logger.info('The return code : %d and text : %s', code, text)
        return code, text 
