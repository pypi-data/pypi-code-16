import threading

from concurrentfloodscraper.router import RouteManager
from concurrentfloodscraper.scraper import Scraper


class BaseWorker(threading.Thread):
    parse_class = Scraper

    def __init__(self, tid, context):
        super().__init__()
        self.tid = tid
        self.context = context

    def run(self):
        while True:
            # get new url
            new_url = self.context.pubsub.pop()

            # parse
            # im not sure if i should feel ashamed or proud
            # its probably ashamed :(
            # ...
            # parser_cls = RouteManager.route(new_url)
            # new_urls = parser_cls(new_url).parse()
            new_urls = RouteManager.route(new_url)(new_url).parse()

            # add new urls to master urls queue
            self.context.pubsub.push_group(new_urls)

            # check exit condition
            if self.context.is_done():
                return
