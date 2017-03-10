#!/usr/bin/env python3
#
####################################################################
#
# Copyright (c) 2017 Timothy H. Lee
# All Rights Reserved.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the Apache License 2.0 License.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, 
# EXPRESS OR IMPLIED. See the Apache License 2.0 License for 
# more details.
#
####################################################################

from html.parser import HTMLParser
from urllib import parse
from urllib.request import urlopen
import re
import logging
from operator import itemgetter
import nltk
from pprint import PrettyPrinter
import argparse

############################################################
#
# Class to analyze word count dictionary for keywords,
# adverbs, adjectives, verbs and nouns
#
############################################################
class Analytics:
    def __init__(self, keyword_file):
        self.keyword_file = keyword_file
        self.keywords = set()
        self.keywords_count = []
        self.nltk_processed = []
        self.load_keywords()

    ################################################
    # read keywords, one per line, from keyword_file
    ################################################
    def load_keywords(self):
        try:
            file = open(self.keyword_file, 'r')
        except OSError as ex:
            logging.error("Failed to open keyword file: {}, error: {}".format(self.keyword_file, ex))
            return

        for line in file:
            self.keywords.add(line.strip())
    ########################################################
    # Analyze and sort words from wordlist dictionary.
    # keys are the words and values the counts for each word.
    ########################################################
    def process(self, wordlist):
        self.set_keyword_count(wordlist)
        self.nltk_process(wordlist)

    #############################
    # sort keywords by word count
    #############################
    def set_keyword_count(self, wordlist):
        self.keywords_count = []
        for keyword in self.keywords:
            try:
                self.keywords_count.append((keyword, wordlist[keyword]))
            except KeyError:
                pass

        self.keywords_count.sort(key=itemgetter(1), reverse=True)
    
    ########################################################
    # determine part of speech (POS) for each word and store 
    # as tuple in nltk_processed: (word, cound, POS)
    ########################################################
    def nltk_process(self, wordlist):
        try:
            self.nltk_processed = [( x[0], wordlist[x[0]], x[1]) for x in nltk.pos_tag(list(wordlist.keys()))]
        except Exception as ex:
            logging.error("NLTK processing error, maxent_treebank_pos_tagger not installed? : {}".format(ex))
            raise ex
 
    #################################
    # return dictionary of verbs with 
    # word as key and count as value 
    #################################
    def get_verbs(self):
        return self.get_pos("VB")

    #################################
    # return dictionary of nouns with 
    # word as key and count as value 
    #################################
    def get_nouns(self):
        return self.get_pos("NN")

    ######################################
    # return dictionary of adjectives with 
    # word as key and count as value 
    ######################################
    def get_adjectives(self):
        return self.get_pos("JJ")

    ###################################
    # return dictionary of adverbs with 
    # word as key and count as value 
    ###################################
    def get_adverbs(self):
        return self.get_pos("RB")

    ###################################
    # return dictionary of POS with 
    # word as key and count as value 
    ###################################
    def get_pos(self, pos_abr):
        words=[(x[0], x[1]) for x in self.nltk_processed if x[2].startswith(pos_abr)]
        words.sort(key=itemgetter(1), reverse=True)
        return words

##################################
# Class to represent an HTML page
##################################
class Page(HTMLParser):
    def __init__(self, base_url):
        super().__init__()
        logging.info("New page at: %s", base_url)
        self.base_url = base_url
        self.wordcount = dict()
        self.links = []
        self.wordMatch = re.compile("^[\w.,;:?!]+$")
        self.stripPunct = re.compile("[\.,;:?!]")

    ####################
    # find links on page
    ####################
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (name, value) in attrs:
                if name == 'href':
                    new_url = parse.urljoin(self.base_url, value)
                    logging.debug("Adding url %s", new_url)
                    self.links.append(new_url)

    #####################
    # count words on page
    #####################
    def handle_data(self, data):
        logging.debug("got data %s", data)
        for word in [self.stripPunct.sub("",x.lower()) for x in data.split() if self.wordMatch.match(x)]:
            logging.debug("got word %s", word)
            if word in self.wordcount:
                self.wordcount[word] += 1
            else:
                self.wordcount[word] = 1

####################################
# Class to crawl web pages on a site
####################################
class Crawler:
    def __init__(self, base_url, maxdepth, url_pattern):
        self.base_url = base_url
        self.hostname = parse.urlparse(base_url)[1]
        self.url_pattern = re.compile(url_pattern)
        self.maxdepth = maxdepth
        logging.info("New Crawler, base_url: %s, maxdepth: %s, url_pattern: %s", base_url, maxdepth, url_pattern)

    #########################################
    # initialize varialbes and start crawling
    #########################################
    def start(self):
        logging.info("Starting new crawl")
        self.depth = 0
        self.wordcount = dict()
        self.pagecount = 0
        self.visited = set()
        self.crawl(self.base_url)

    #############################################
    # count words on each page called recursively
    #############################################
    def crawl(self, url):
        response = urlopen(url)
        if response.getheader('Content-Type') == 'text/html; charset=utf-8':
            logging.debug("New web page at: %s", url)
            self.pagecount += 1
            bytes = response.read()
            text = bytes.decode('utf-8')
            logging.debug("text \n%s\n\n\n", text)
            page = Page(url)
            page.feed(text)
            logging.debug("Adding %s words.", len(page.wordcount.keys()))
            self.updateWordcount(page.wordcount)
            if self.depth < self.maxdepth:
                for link in [x for x in page.links if self.proceed(x)]:
                    self.visited.add(link)
                    self.depth += 1
                    logging.debug("Crawling link: '%s', depth: %s, page count: %s", link, self.depth, self.pagecount)
                    self.crawl(link)
                    self.depth -= 1


    #################################
    # Determine whether to crawl link
    #################################
    def proceed(self, url):
        if self.hostname != parse.urlparse(url)[1]:
            return False

        if url in self.visited:
            return False

        if self.url_pattern.search(url):
            return True
        else:
            return False

    ###############################
    # Update word count for session
    ###############################
    def updateWordcount(self, updateWordcount):
        for (word, count) in updateWordcount.items():
            if word in self.wordcount:
                self.wordcount[word] += count
            else:
                self.wordcount[word] = count

###############################################
# main function to parse command line arguments
# crawl web site and print output
###############################################
def main():
    """
    analyze_site.py -d 1 -r 'technology\/\w' software_keywords.txt 'http://careers.vistaprint.com/search?searchCulture=en&searchText=&searchCareerTracks=Technology&searchLocations=Waltham'
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("keywords_file", help="Path to keywords file")
    parser.add_argument("url", help="URL to crawl")
    parser.add_argument("-d", "--depth", help="Depth to crawl", type=int, default=1)
    parser.add_argument("-r", "--path_regex", help="Regular expression to match URL", default=".")
    parser.add_argument("--verbose", help="Increase logging level", action="store_true")
    args = parser.parse_args()
    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG

    logging.basicConfig(filename="/tmp/crawl.log", level=log_level)
    logging.info("Starting crawl-site.py")
    POS_CUTOFF = 15
    crawler = Crawler(args.url, args.depth, args.path_regex)
    crawler.start()
    #analytics = Analytics("./software-keywords.txt")
    analytics = Analytics(args.keywords_file)
    analytics.process(crawler.wordcount)
    pp = PrettyPrinter()
    print("\nKeywords\n--------------------")
    pp.pprint(analytics.keywords_count)
    print("\nTop Verbs\n--------------------")
    pp.pprint(analytics.get_verbs()[:POS_CUTOFF])
    print("\nTop Nouns\n--------------------")
    pp.pprint(analytics.get_nouns()[:POS_CUTOFF])
    print("\nTop Adverbs\n--------------------")
    pp.pprint(analytics.get_adverbs()[:POS_CUTOFF])
    print("\nTop Adjectives\n--------------------")
    pp.pprint(analytics.get_adjectives()[:POS_CUTOFF])

if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        print("Execution error: {}".format(ex))
        
