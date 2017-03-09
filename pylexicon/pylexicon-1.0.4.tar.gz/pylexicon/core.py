import re
import requests
from bs4 import BeautifulSoup


def _get_soup_object(url, parser="html.parser"):
    return BeautifulSoup(requests.get(url).text, parser)


def define(word):
    """ Looks up and defines a word
        Args:
            word: a single word string

        Returns:
            A dictionary
            {'type of word':['Definition 1', 'Definition 2']}

        Example:
            define('hello')
            {'Noun': ['an expression of greeting']}
    """

    if len(word.split()) > 1:
        raise ValueError("Search must only be one word")

    html = _get_soup_object(
        "http://wordnetweb.princeton.edu/perl/webwn?s=" + word)

    types = html.findAll('h3')
    lists = html.findAll('ul')
    meaning = {}

    for item in types:
        reg = str(lists[types.index(item)])
        meanings = []
        for x in re.findall(r'> \((.*?)\) <', reg):
            if 'often followed by' in x:
                pass

            elif len(x) > 5 or ' ' in str(x):
                meanings.append(x)

        name = item.text
        meaning[name] = meanings

    return meaning


def synonym(word):
    """ Looks up and returns synonyms of a word
        Args:
            word: a single word string

        Returns:
            A list of synonyms
            ['synonym 1', 'synonym 2']

        Example:
            synonym('hello')
            ['welcome', 'howdy', 'hi', 'greetings', 'bonjour']
    """

    if len(word.split()) > 1:
        raise ValueError("Search must only be one word")

    html = _get_soup_object("http://www.thesaurus.com/browse/" + word)
    terms = html.select("div#filters-0")[0].findAll("li")

    if len(terms) > 5:
        terms = terms[:5]       # Shorten the list to five synonyms

    similars = []

    for item in terms:
        similars.append(item.select("span.text")[0].getText())

    return similars


def antonym(word):
    """ Looks up and returns antonyms of a word
        Args:
            word: a single word string

        Returns:
            A list of antonyms
            ['antonym 1', 'antonym 2']

        Example:
            antonym('hello')
            ['adios', 'au revoir', 'goodbye']
    """

    if len(word.split()) > 1:
        raise ValueError("Search must only be one word")

    html = _get_soup_object("http://www.thesaurus.com/browse/" + word)

    terms = html.select("section.antonyms")[0].findAll("li")

    if len(terms) > 5:
        terms = terms[:5]       # Shorten the list to five antonyms

    opposites = []
    for item in terms:
        opposites.append(item.select("span.text")[0].getText())

    return opposites
