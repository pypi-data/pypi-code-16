# ----------------------------------------------------------------------------
# pyPodCatch: Simple podcast fetching and tagging
# Copyright (c) 2016-2017 Jules Lallouette
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------
from Episode import *
from Parameters import *
from Utilities import *

import feedparser
import os
from os import mkdir, remove, path

tmpFeedFilePath = u'feed.xml'
epListFileName = u'episodes.dat'

class Podcast:
	def __init__(self, url, specifNbr = None, podcastDirPath = defaultPodDirPath):
		self.parser = None
		self.loadedFromFile = False
		if specifNbr:
			self.maxNbEpisodes = specifNbr
		else:
			self.maxNbEpisodes = maxNbEpisodes
		self.LoadXML(url)
		# Fill values
		if 'title' in self.parser.feed:
			self.title = self.parser.feed.title
		else:
			self.title = defaultPodcastTitle

		if 'author' in self.parser.feed:
			self.author = self.parser.feed.author
		else:
			self.author = defaultPodcastAuthor

		self.dirPath = podcastDirPath + self.title.replace(u'/', u'_') + u'/'
		try:
			os.makedirs(self.dirPath)
			print(u"Directory created")
		except OSError as ex:
			if not os.path.exists(self.dirPath):
				if os.path.exists(podcastDirPath):
					print(u"Error, could not create: " + self.dirPath + u":" + unicode(ex))
				else:
					print(u"The podcast directory " + podcastDirPath + " does not exist.")
				raise

		try:
			if ('image' in self.parser.feed) and ('href' in self.parser.feed.image):
				self.imgURL = self.parser.feed.image['href']
			self.imgPath = self.dirPath + defaultImgName + u'.' + self.imgURL.split(u'.')[-1]
			FetchFile(self.imgURL, self.imgPath)
		except:
			self.imgURL = u''

		self.episodes = []
		xmlEpisodes = self.parser.entries
		print(unicode(len(xmlEpisodes)) + u" entries parsed.")
		# Load previously loaded episodes
		podFilePath = self.dirPath + epListFileName
		if os.path.exists(podFilePath):
			print(u'Loading "' + podFilePath + u'"...')
			self.LoadEpisodesFromFile(self.dirPath + epListFileName)

		nbNewEp = 0
		for xmlEp in xmlEpisodes:
			# audio only - skip the videos
			for (ind, encl) in enumerate(xmlEp.enclosures):
				if ('type' in encl) and (encl['type'] == u'audio/mpeg'):
					ep = Episode(self, xmlEp, ind)
					if not ep.IsPresentIn(self.episodes):
						nbNewEp += 1
						self.episodes.append(ep)
		if nbNewEp == 0:
			print(u"No new episodes were published.")

		# Order by publication date
		self.OrderEpisodes()

		# If some episodes have already been fetched, fetch all the new ones
		if self.loadedFromFile:
			startInd = 0
			for (ind, ep) in enumerate(self.episodes):
				if ep.filePath != u'':
					startInd = ind
					break
			if (startInd > len(self.episodes) - self.maxNbEpisodes) or (self.maxNbEpisodes == -1):
				startInd = max(0, len(self.episodes) - self.maxNbEpisodes) if self.maxNbEpisodes > -1 else 0
		# Otherwise, only fetch a limited number of episodes
		else:
			startInd = max(0, len(self.episodes) - self.maxNbEpisodes) if self.maxNbEpisodes > -1 else 0
		for ep in self.episodes[startInd:]:
			ep.FetchURL()

	def LoadXML(self, url):
		print(u"Fetching " + url + u" ...")
		FetchFile(url, tmpFeedFilePath)
		print(u"Done.")
		try:
			self.parser = feedparser.parse(tmpFeedFilePath)
		except Exception as ex:
			print(u"Couldn't parse " + url + u":" + unicode(ex))
		os.remove(tmpFeedFilePath)

	def LoadEpisodesFromFile(self, filePath):
		epListFile = open(filePath, 'r')
		nbEp = int(epListFile.readline().strip('\n'))
		for i in range(nbEp):
			self.episodes.append(Episode(self))
			self.episodes[-1].LoadFromFile(epListFile)
		epListFile.close()
		self.loadedFromFile = True

	def SaveEpisodesToFile(self, filePath):
		epListFile = open(filePath, 'w')
		epListFile.write(str(len(self.episodes)) + '\n')
		for ep in self.episodes:
			ep.SaveToFile(epListFile)
		epListFile.close()
		
	def OrderEpisodes(self):
		self.episodes = sorted(self.episodes, key = lambda ep: ep.pubDate)
		for (num, ep) in enumerate(self.episodes, 1):
			ep.num = num

	def UpdateTags(self, filts=None):
		print(u"Updating tags...")
		nbUp = 0
		nbFailed = 0
		for ep in self.episodes:
			if ep.filePath != u'':
				if not ep.UpdateTag(filts):
					nbFailed += 1
				nbUp += 1
		if nbFailed == 0:
			if nbUp > 0:
				print(u"Tags from " + unicode(nbUp) + u" files updated successfully.")
			else:
				print(u"No tags to update.")
		else:
			print(unicode(nbFailed) + u"/" + unicode(nbUp) + u" tags were not saved correctly.")

	def Save(self):
		self.SaveEpisodesToFile(self.dirPath + epListFileName)

