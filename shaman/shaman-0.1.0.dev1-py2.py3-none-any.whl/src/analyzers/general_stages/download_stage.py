import grab
import pickle
import datetime

from grab.error import GrabTimeoutError, GrabCouldNotResolveHostError, GrabNetworkError, GrabTooManyRedirectsError

from shaman.src.analyzers.abstract_stage import AbstractStage


class DownloadStage(AbstractStage):
    """
    Trying to download page. If this operation is successful, adds a result to a message.
    If there is an exception (could be a network problem or grab timeout), or http response code != 200,
    adds information about it to the results.
    Later, depending on the result of this stage, data is sending in kafka (if success) or sending to mongo (vice versa).

    Input data:
        - url
    Output data:
        - output_dict

    Using python modules:
        - grab (to download)
        - pickle (to serialize)
        - datetime (to add an operation date)
    """
    def __init__(self, config):
        self.order = config['order']
        self.grab_connect_timeout = int(config['connect_timeout'])
        self.grab_download_timeout = int(config['download_timeout'])
        self.grab = grab.Grab()
        self.grab.setup(connect_timeout=self.grab_connect_timeout, timeout=self.grab_download_timeout)
        self.proxy_list_filename = ''


    def do_stage(self, message):
        url = message.url

        try:
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

            message.inc_field = 'retries'



        return message