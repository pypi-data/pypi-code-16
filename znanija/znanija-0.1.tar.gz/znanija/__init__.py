import requests
from bs4 import BeautifulSoup
from collections import namedtuple


Task = namedtuple('Task', 'description link')


class Scraper():
    """Class used to scrape needed data from HTML source."""
    def __init__(self, page='http://znanija.com/predmet/informatika'):
        self._page = page
        self.__session = requests.Session()
        self.__session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
        })

    @property
    def page(self):
        return self._page

    @page.setter
    def page(self, v):
        self._page = v

    @property
    def keyword(self):
        return self._keyword

    @keyword.setter
    def keyword(self, v):
        self._keyword = v

    def get(self):
        return self.__session.get(self._page).text


class Parser():
    """Class used to parse data from Scraper."""
    def __init__(self, html=None, basename='znanija.com'):
        self._html = html
        self._basename = basename
        if self._html:
            self.update_soup(self._html)

    @property
    def html(self):
        return self._html

    @html.setter
    def html(self, v):
        self._html = v
        self.update_soup(self._html)

    def update_soup(self, html):
        self._soup = BeautifulSoup(html, "lxml")

    def find_containing(self, keywords):
        results = []
        task_list = self._soup.find('div', {'class': 'js-main-stream'})
        tasks = task_list.find_all('article', {'class': 'task'})
        for task in tasks:
            task_heading = task.find('a', {'class': 'sg-text'})
            task_description = task_heading.text.strip()
            task_link = task_heading.get('href')
            if not self._basename in task_link:
                task_link = 'http://' + self._basename + task_link
            if any(word.upper() in task_description.upper() for word in keywords):
                results.append(Task(description=task_description, link=task_link))
        return results


class Znanija():
    """Class to easily control and maintain actions for znanija.com."""
    def __init__(self,
                 predmet='informatika',
                 keywords=['python', 'c++', 'java', 'c#'],
                 html=None):
        self.predmet = predmet
        self.keywords = keywords
        pagename = 'http://znanija.com/predmet/' + predmet
        print(pagename)
        self._scraper = Scraper(page=pagename)
        self._parser = Parser()
        self.update_html()

    def update_html(self):
        self._parser.html = self._scraper.get()

    def tasks_containing_keywords(self, keywords=None):
        self.update_html()
        keywords = keywords if keywords else self.keywords
        return self._parser.find_containing(keywords)
