import httplib2
import json
import logging

class Push_client(object):
  logger = logging.getLogger(__name__)
  def __init__(self, url):
    self.url = url
    self.logger.info("Push_client configured to {}".format(self.url))

  def push_data(self, data_to_push):
    if not self.url:
      logging.warning("no url set, push ignored")
    else:
      json_to_send = json.dumps(data_to_push)
      h = httplib2.Http()
      self.logger.debug("sending {} to server {}".format(data_to_push, self.url))
      (resp_headers, _) = h.request(self.url, body=json_to_send, method="PUT",
                                    headers={'Content-Type': 'application/json'})

      if resp_headers.status != 200:
        logging.warning("server returns {}".format(resp_headers.status))
