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
from Utilities import *
from Parameters import *
import dateutil.parser
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
import mutagen
import os
from os import path

EasyID3.RegisterTextKey("albumartist", "TPE2")

class Episode:
	def __init__(self, podcast, xmlEp = None, enclInd = 0):
		self.podcast = podcast
		self.filePath = u''
		if xmlEp:
			# Get the podcast attributes
			self.title = xmlEp.title
			if 'href' in xmlEp.enclosures[enclInd]:
				self.url = xmlEp.enclosures[enclInd]['href']
			elif 'url' in xmlEp.enclosures[enclInd]:
				self.url = xmlEp.enclosures[enclInd]['url']
			else:
				self.url = u''
			if 'author' in xmlEp:
				self.author = xmlEp.author
			else:
				self.author = u''
			self.pubDateStr = xmlEp.published
			self.pubDate = dateutil.parser.parse(self.pubDateStr)
			self.num = -1

	def LoadFromFile(self, fileObj):
		self.title = fileObj.readline().strip('\n').decode('utf8')
		self.url = fileObj.readline().strip('\n').decode('utf8')
		self.author = fileObj.readline().strip('\n').decode('utf8')
		self.pubDateStr = fileObj.readline().strip('\n').decode('utf8')
		self.pubDate = dateutil.parser.parse(self.pubDateStr)
		self.filePath = fileObj.readline().strip('\n').decode('utf8')
		self.num = int(fileObj.readline().strip('\n'))

	def SaveToFile(self, fileObj):
		fileObj.write(self.title.encode('utf8') + '\n')
		fileObj.write(self.url.encode('utf8') + '\n')
		fileObj.write(self.author.encode('utf8') + '\n')
		fileObj.write(self.pubDateStr.encode('utf8') + '\n')
		fileObj.write(self.filePath.encode('utf8') + '\n')
		fileObj.write(str(self.num) + '\n')

	def FetchURL(self):
		if self.filePath == u'':
			print(u"Fetching " + self.url + u" ...")
			self.filePath = self.podcast.dirPath + self.title.replace(' ', '_').replace('/', '_') + u'.' + self.url.split(u'.')[-1]
			if not FetchFile(self.url, self.filePath):
				self.filePath = u''
				print(u"Failed.")
			else:
				self.fetched = True
				print(u"Done.")
	
	def IsPresentIn(self, epList):
		for ep in epList:
			if (ep.url == self.url) or ((ep.pubDate == self.pubDate) and (ep.title == self.title)):
				return True
		return False

	def applyFilts(self, tags, field, content, filts):
		if field in filts:
			tags[field] = re.sub(filts[field][0], filts[field][1], content)
		else:
			tags[field] = content

	def UpdateTag(self, filts=None):
		if self.filePath != u'':
			tags = None
			if os.path.splitext(self.filePath)[1] == '.mp3':
				try:
					tags = EasyID3(self.filePath)
				except mutagen.id3.ID3NoHeaderError:
					try:
						tags = mutagen.File(self.filePath, easy=True)
						tags.add_tags()
					except Exception as ex:
						print(u"Error while loading mp3 tags for " + self.filePath + u": " + unicode(ex))
						return False
			elif os.path.splitext(self.filePath)[1] == '.flac':
				try:
					tags = FLAC(self.filePath)
				except Exception as ex:
					print(u"Error while loading flac tags for " + self.filePath + u": " + unicode(ex))
					return False
			else:
				print(u"File extension not supported: " + unicode(self.filePath))
				return False
			
			try:
				self.applyFilts(tags, 'albumartist', self.podcast.author, filts)
				if self.author != u'':
					self.applyFilts(tags, 'artist', self.author, filts)
				else:
					self.applyFilts(tags, 'artist', self.podcast.author, filts)
				self.applyFilts(tags, 'title', self.title, filts)
				self.applyFilts(tags, 'album', self.podcast.title, filts)
				self.applyFilts(tags, 'tracknumber', unicode(self.num), filts)
				self.applyFilts(tags, 'genre', defaultGenre, filts)
				self.applyFilts(tags, 'date', unicode(self.pubDate.year), filts)
				tags.save()
			except Exception as ex:
				print(u"Couldn't add tag to " + self.filePath + u": " + unicode(ex))
				return False

		return True
