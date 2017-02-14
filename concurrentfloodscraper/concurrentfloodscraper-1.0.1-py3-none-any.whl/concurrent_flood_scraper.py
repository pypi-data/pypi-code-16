from concurrentfloodscraper.base_controller import BaseController
from concurrentfloodscraper.scraper import Scraper


# easy way to extend functionality
class ConcurrentFloodScraper:
    parser_class = Scraper

    def __init__(self, root, num_workers, num_pages):
        self.controller = BaseController(num_workers)
        self.controller.worker_class.parse_class = self.parser_class
        self.root = root
        self.num_pages = num_pages

    def start(self):
        self.controller.start(self.root, self.num_pages)

    def join(self):
        self.controller.join()
