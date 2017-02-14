from concurrentfloodscraper import ConcurrentFloodScraper, Route, Scraper


# route all urls that match wikipedia articles to this scraper
@Route(r'^https?://en.wikipedia.org/wiki/[^\s]+$')
class WikipediaScraper(Scraper):
    # we only want other urls that match wikipedia articles
    url_filter_regex = r'^https?://en.wikipedia.org/wiki/[^\s]+$'

    def scrape_page(self, text):
        pass
        # TODO parse logic goes here


def run():
    # define starting url
    ROOT = 'https://en.wikipedia.org/wiki/Main_Page'

    # instatiate pool, 10 threads, 500 page limit
    pool = ConcurrentFloodScraper(ROOT, 10, 500)

    # start
    pool.start()

    # wait for 500 pages to be done
    pool.join()

    # we made it
    print('Done!')


if __name__ == '__main__':
    run()
