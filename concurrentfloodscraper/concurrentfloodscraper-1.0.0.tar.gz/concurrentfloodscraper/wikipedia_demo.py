from concurrentfloodscraper import ConcurrentFloodScraper, Route, Scraper


@Route(r'^https?://en.wikipedia.org/wiki/[^\s]+$')
class WikipediaScraper(Scraper):
    url_filter_regex = r'^https?://en.wikipedia.org/wiki/[^\s]+$'

    def scrape_page(self, text):
        pass
        # TODO parse logic goes here


def run():
    ROOT = 'https://en.wikipedia.org/wiki/Main_Page'
    pool = ConcurrentFloodScraper(ROOT, 10, 500)
    pool.start()
    pool.join()
    print('Done!')
