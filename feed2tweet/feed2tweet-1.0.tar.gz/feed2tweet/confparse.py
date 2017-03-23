# -*- coding: utf-8 -*-
# Copyright © 2015-2017 Carl Chenet <carl.chenet@ohmytux.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/

# Get values of the configuration file
'''Get values of the configuration file'''

# standard library imports
from configparser import SafeConfigParser, NoOptionError, NoSectionError
import logging
import os
import os.path
import socket
import sys

# 3rd party library imports
import feedparser

class ConfParse(object):
    '''ConfParse class'''
    def __init__(self, clioptions):
        '''Constructor of the ConfParse class'''
        self.clioptions = clioptions
        self.tweetformat = ''
        self.stringsep = ','
        self.confs = []
        self.main()

    def main(self):
        '''Main of the ConfParse class'''
        for pathtoconfig in self.clioptions.configs:
            options = {}
            # read the configuration file
            config = SafeConfigParser()
            if not config.read(os.path.expanduser(pathtoconfig)):
                sys.exit('Could not read config file')
            ###########################
            # 
            # the rss section
            # 
            ###########################
            section = 'rss'
            if config.has_section(section):
                ############################
                # tweet option
                ############################
                confoption = 'tweet'
                if config.has_option(section, confoption):
                    self.tweetformat = config.get(section, confoption)
                else:
                    sys.exit('You should define a format for your tweet with the keyword "tweet" in the [rss] section')
                ############################
                # pattern format option
                ############################
                options['patterns'] = {}
                options['patternscasesensitive'] = {}
                for pattern in ['summary_detail', 'published_parsed', 'guidislink', 'authors', 'links', 'title_detail', 'author', 'author_detail', 'comments', 'published', 'summary', 'tags', 'title', 'link', 'id']:
                    currentoption = '{}_pattern'.format(pattern)
                    if config.has_option(section, currentoption):
                        tmppattern = config.get(section, currentoption)
                        if self.stringsep in tmppattern:
                            options['patterns'][currentoption] = [i for i in tmppattern.split(self.stringsep) if i]
                        else:
                            options['patterns'][currentoption] = [tmppattern]

                    # pattern_case_sensitive format
                    currentoption = '{}_pattern_case_sensitive'.format(pattern)
                    if config.has_option(section, currentoption):
                        try:
                            options['patternscasesensitive'][currentoption] = config.getboolean(section, currentoption)
                        except ValueError as err:
                            print(err)
                            options['patternscasesensitive'][currentoption] = True
                ############################
                # rsslist
                ############################
                bozoexception = False
                feeds = []
                patterns = []
                currentoption = 'uri_list'
                if config.has_option(section, currentoption):
                    rssfile = config.get(section, currentoption)
                    rssfile = os.path.expanduser(rssfile)
                    if not os.path.exists(rssfile) or not os.path.isfile(rssfile):
                        sys.exit('The path to the uri_list parameter is not valid: {rssfile}'.format(rssfile=rssfile))
                    rsslist = open(rssfile, 'r').readlines()
                    for line in rsslist:
                        line = line.strip()
                        # split each line in two parts, rss link and a string with the different patterns to look for
                        confobjects = line.split('|')
                        if len(confobjects) > 3 or len(confobjects) == 2:
                            sys.exit('This line in the list of uri to parse is not formatted correctly: {line}'.format(line))
                        if len(confobjects) == 3:
                            rss, rssobject, patternstring = line.split('|')
                        if len(confobjects) == 1:
                            rss = confobjects[0]
                            rssobject = ''
                            patternstring = ''
                        # split different searched patterns
                        patterns = [i for i in patternstring.split(self.stringsep) if i]
                        # retrieve the content of the rss
                        feed = feedparser.parse(rss)
                        if 'bozo_exception' in feed:
                            bozoexception = True
                            logging.warning(feed['bozo_exception'])
                            continue
                        # check if the rss feed and the rss entry are valid ones
                        if 'entries' in feed:
                            if rssobject and rssobject not in feed['entries'][0].keys():
                                sys.exit('The rss object {rssobject} could not be found in the feed {rss}'.format(rssobject=rssobject, rss=rss))
                        else:
                            sys.exit('The rss feed {rss} does not seem to be valid'.format(rss=rss))
                        feeds.append({'feed': feed, 'patterns': patterns, 'rssobject': rssobject})
                    # test if all feeds in the list were unsuccessfully retrieved and if so, leave
                    if not feeds and bozoexception:
                        sys.exit('No feed could be retrieved. Leaving.')
                ############################
                # uri
                ############################
                if not feeds and not self.clioptions.rss_uri:
                    confoption = 'uri'
                    if config.has_option(section, confoption):
                        options['rss_uri'] = config.get('rss', 'uri')
                    else:
                        sys.exit('{confoption} parameter in the [{section}] section of the configuration file is mandatory. Exiting.'.format(section=section, confoption=confoption))
                else:
                    options['rss_uri'] = self.clioptions.rss_uri
                # get the rss feed for rss parameter of [rss] section
                feed = feedparser.parse(options['rss_uri'])
                if not feed:
                    sys.exit('Unable to parse the feed at the following url: {rss}'.format(rss=rss))

                #########################################
                # no_uri_pattern_no_global_pattern option
                #########################################
                currentoption = 'no_uri_pattern_no_global_pattern'
                # default value
                options['nopatternurinoglobalpattern'] = False
                if config.has_option(section, currentoption):
                    options['nopatternurinoglobalpattern'] = config.getboolean(section, currentoption)
            ###########################
            # 
            # the cache section
            # 
            ###########################
            section = 'cache'
            if not self.clioptions.cachefile:
                confoption = 'cachefile'
                if config.has_section(section):
                    options['cachefile'] = config.get(section, confoption)
                else:
                    sys.exit('You should provide a {confoption} parameter in the [{section}] section'.format(section=section, confoption=confoption))
                options['cachefile'] = os.path.expanduser(options['cachefile'])
                cachefileparent = os.path.dirname(options['cachefile'])
                if cachefileparent and not os.path.exists(cachefileparent):
                    sys.exit('The parent directory of the cache file does not exist: {cachefileparent}'.format(cachefileparent=cachefileparent))
            else:
                options['cachefile'] = self.clioptions.cachefile
            ### cache limit
            if config.has_section(section):
                confoption = 'cache_limit'
                if config.has_option(section, confoption):
                    try:
                        options['cache_limit'] = int(config.get(section, confoption))
                    except ValueError as err:
                        sys.exit('Error in configuration with the {confoption} parameter in [{section}]: {err}'.format(confoption=confoption, section=section, err=err))
                else:
                    options['cache_limit'] = 100
            else:
                options['cache_limit'] = 100
            ###########################
            # 
            # the hashtag section
            # 
            ###########################
            section = 'hashtaglist'
            if not self.clioptions.hashtaglist:
                confoption = 'several_words_hashtags_list'
                if config.has_section(section):
                    options['hashtaglist'] = config.get(section, confoption)
                    options['hashtaglist'] = os.path.expanduser(options['hashtaglist'])
                    if not os.path.exists(options['hashtaglist']) or not os.path.isfile(options['hashtaglist']):
                        sys.exit('The path to the several_words_hashtags_list parameter is not valid: {hashtaglist}'.format(hashtaglist=options['hashtaglist']))
                else:
                    options['hashtaglist'] = False
            ###########################
            # 
            # the plugins section
            # 
            ###########################
            plugins = {}
            section = 'influxdb'
            if config.has_section(section):
                ##########################################
                # host, port, user, pass, database options
                ##########################################
                plugins[section] = {}
                for currentoption in ['host','port','user','pass','database']:
                    if config.has_option(section, currentoption):
                        plugins[section][currentoption] = config.get(section, currentoption)
                if 'host' not in plugins[section]:
                    plugins[section]['host'] = '127.0.0.1'
                if 'port' not in plugins[section]:
                    plugins[section]['port'] = 8086
                if 'measurement' not in plugins[section]:
                    plugins[section]['measurement'] = 'tweets'
                for field in ['user','pass','database']:
                    if field not in plugins[section]:
                        sys.exit('Parsing error for {field} in the [{section}] section: {field} is not defined'.format(field=field, section=section))

            # create the returned object with previously parsed data
            if feeds:
                self.confs.append((options, config, self.tweetformat, feeds, plugins))
            else:
                self.confs.append((options, config, self.tweetformat, [{'feed': feed, 'patterns': [], 'rssobject': ''}], plugins))
        
    @property
    def confvalues(self):
        '''Return the values of the different configuration files'''
        return self.confs
