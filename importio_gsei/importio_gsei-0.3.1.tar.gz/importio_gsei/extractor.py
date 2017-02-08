#
# Copyright 2016 Import.io
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import requests
import os
import logging
import json

logger = logging.getLogger(__name__)


class Extractor(object):
    def __init__(self, extractor_id):
        self._extractor_id = extractor_id
        self._api_key = os.environ['IMPORT_IO_API_KEY']


class ExtractorGet(Extractor):
    def __init__(self, extractor_id):
        super(ExtractorGet, self).__init__(extractor_id)

    def get(self):
        url = "https://store.import.io/store/extractor/{0}".format(self._extractor_id)

        querystring = {
            "_apikey": self._api_key
        }

        headers = {
            'cache-control': "no-cache",
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        logger.debug(response.text)
        return response.json()


class ExtractorGetUrlList(Extractor):
    def __init__(self, extractor_id):
        super(ExtractorGetUrlList, self).__init__(extractor_id)

    def get(self):
        """
        Call the Extractor API to return the URLs associated with an extractor
        :return:  array of str
        """
        api = ExtractorGet(extractor_id=self._extractor_id)

        extractor = api.get()

        url = "https://store.import.io/store/extractor/{0}/_attachment/urlList/{1}".format(
            self._extractor_id, extractor['urlList'])
        querystring = {
            "_apikey": self._api_key
        }

        headers = {
            'accept-encoding': "gzip",
            'cache-control': "no-cache",
        }
        logger.debug("url: ".format(url))
        response = requests.request("GET", url, headers=headers, params=querystring)

        logger.debug(response.text)
        return response.text.split('\n')


class ExtractorPutUrlList(Extractor):
    def __init__(self, extractor_id):
        super(ExtractorPutUrlList, self).__init__(extractor_id)

    def put(self, urls):
        """
        Calls the Extractor API with a list of URLs to associate with an extractor
        :param urls: array of str containing the URLs
        :return: None
        """
        url = "https://store.import.io/store/extractor/{0}/_attachment/urlList".format(self._extractor_id)

        querystring = {
            "_apikey": self._api_key
        }

        headers = {
            'content-type': "text/plain"
        }

        logger.debug("urls ({0}): {1}".format(type(urls), urls))

        data = "\n".join(urls)

        response = requests.request("PUT", url, data=data, headers=headers, params=querystring)


class ExtractorStart(Extractor):
    """
    Starts an Extractor running
    """

    def __init__(self, extractor_id):
        super(ExtractorStart, self).__init__(extractor_id)

    def start(self):
        """
        Initiate a crawl-run by an Extractor

        :return:
        """
        url = "https://run.import.io/{0}/start".format(self._extractor_id)

        querystring = {
            "_apikey": self._api_key
        }

        headers = {
            'cache-control': "no-cache",
        }

        response = requests.request("POST", url, headers=headers, params=querystring)

        if response.status_code == requests.codes.ok:
            result = response.json()['crawlRunId']
        else:
            result = response.json()
        return result


class ExtractorStatus(Extractor):

    def __init__(self, extractor_id):
        super(ExtractorStatus, self).__init__(extractor_id)

    def get(self):
        logging.basicConfig(level=logging.DEBUG)
        url = "https://store.import.io/store/crawlrun/_search"

        querystring = {"_sort": "_meta.creationTimestamp", "_page": "1", "_perPage": "30",
                       "extractorId": self._extractor_id,
                       "_apikey": self._api_key
                       }

        headers = {
            'cache-control': "no-cache",
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        results = response.json()
        crawl_runs = []
        for run in results['hits']['hits']:
            r = {}
            r['guid'] = run['fields']['guid']
            r['state'] = run['fields']['state']
            r['totalUrlCount'] = run['fields']['totalUrlCount']
            r['successUrlCount'] = run['fields']['successUrlCount']
            r['failedUrlCount'] = run['fields']['failedUrlCount']
            r['rowCount'] = run['fields']['rowCount']
            crawl_runs.append(r)
        return crawl_runs
