import requests as r
import constants as c
from lxml import html

# Entity with utilities for iTunes preview site for Podcasts
class SiteCrawler(object):

  def get_genres(self):
    """Grab (genre,url) tuples from iTunes Podcast preview"""
    page = r.get(c.ITUNES_GENRES_URL)
    tree = html.fromstring(page.content)
    elements = tree.xpath("//a[@class='top-level-genre']")
    return [(e.attrib['title']
              .lower()[:(e.attrib['title'].rfind('-')-1)]
              .replace(' ', ''), e.attrib['href'])
              for e in elements]
