import grab
import pickle
import datetime
import pymongo

from grab.error import GrabTimeoutError, GrabCouldNotResolveHostError, GrabNetworkError, GrabTooManyRedirectsError

from shaman.src.analyzers.abstract_stage import AbstractStage
import random

class DownloadStageProxified(AbstractStage):
    """
    Trying to download page.
    """
    def __init__(self, config):
        self.config = config
        self.order = config['order']
        self.grab_connect_timeout = int(config['connect_timeout'])
        self.grab_download_timeout = int(config['download_timeout'])
        self.mongo_proxy = config['mongo_proxy']
        self.mongo_db = config['mongo_db']
        self.mongo_collection = config['mongo_collection']
        self.proxy_change_every = int(config['proxy_change_every'])
        self.proxy_req_counter = 0
        self.renew_proxy_list_every = int(config['renew_proxy_list_every'])
        self.renew_proxy_list_counter = 0
        self.current_proxy = None

        self.proxy_list = []

        self.renew_proxylist()

        self.setup_grab()

        self.proxy_list_filename = ''

    def setup_grab(self):
        self.grab = grab.Grab()

        self.current_proxy = random.choice(self.proxy_list)
        first_slash_index = self.current_proxy['_id'].find('/')
        proxy_type = self.current_proxy['_id'][:first_slash_index-1]
        proxy_address = self.current_proxy['_id'][first_slash_index+2:]
        proxy_lag = self.current_proxy['latency']

        self.grab.setup(connect_timeout=self.grab_connect_timeout+proxy_lag,
                        timeout=self.grab_download_timeout+proxy_lag,
                        proxy=proxy_address,
                        proxy_type=proxy_type)

    def renew_proxylist(self):
        c = pymongo.MongoClient(self.config['mongo_proxy'])[self.config['mongo_db']][self.config['mongo_collection']]

        self.proxy_list[:] = []
        for p in c.find({'$and':[{'modified_at':{'$gte':datetime.datetime.now()-datetime.timedelta(hours=2)}},
                                 {'latency':{'$lt':5.0}}]}):
            self.proxy_list.append(p)


    def do_stage(self, message):
        url = message.url

        try:
            self.proxy_req_counter+=1
            self.renew_proxy_list_counter+=1

            if self.renew_proxy_list_counter%self.renew_proxy_list_every == 0:
                self.renew_proxylist()
                self.renew_proxy_list_counter = 0

            if self.proxy_req_counter%self.proxy_change_every == 0:
                self.setup_grab()
                self.proxy_req_counter = 0

            response = self.grab.go(url)

            if response.code != 200:
                message.add_result_to_message('_id', message.url, 'failed_urls')
                message.add_result_to_message('owner', message.owner, 'failed_urls')
                message.add_result_to_message('comment', message.comment, 'failed_urls')
                message.add_result_to_message('code', response.code, 'failed_urls')
                message.add_result_to_message('modified_at', datetime.datetime.now(), 'failed_urls')
            else:
                pickled_response = pickle.dumps(response)
                output_dict = {'response': pickled_response,
                               'owner': message.owner,
                               'comment':message.comment,
                               '_id':url}

                output_to_hdfs_dict = {'_id': url,
                                       'html': response.unicode_body(),
                                       'owner': message.owner,
                                       'comment':message.comment}

                message.output_dict = output_dict
                message.output_to_hdfs_dict = output_to_hdfs_dict

                ## this is for saving html in message for future usage
                message.html = response.unicode_body()

            message.response_code = response.code


        except (GrabTimeoutError,
                GrabCouldNotResolveHostError,
                GrabNetworkError,
                GrabTooManyRedirectsError,
                UnicodeDecodeError) as e:

            exception_str = "Unable to download a page, exception: {}".format(str(e))

            message.add_result_to_message('_id', message.url, 'failed_urls')
            message.add_result_to_message('owner', message.owner, 'failed_urls')
            message.add_result_to_message('comment', message.comment, 'failed_urls')
            message.add_result_to_message('exception', exception_str, 'failed_urls')
            message.add_result_to_message('modified_at', datetime.datetime.now(), 'failed_urls')



        return message