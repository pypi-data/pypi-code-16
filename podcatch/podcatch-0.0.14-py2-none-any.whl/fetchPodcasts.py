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

def main():
	from Podcast import Podcast
	from Parameters import defaultPodDirPath, podcastListPath
	import re
	import sys
	import os

	p = re.compile(u'[ \t]*(?:([0-9\-]*)[ \t]+)?(https?://[^ ]*)[ \t\n]*((?:[^"]+ "[^"]*" "[^"]*"[ \t]*)+)?')
	subP = re.compile(u'([^"]+) "([^"]*)" "([^"]*)"[ \t]*')

	if len(sys.argv) > 1:
		podcastListPath = sys.argv[1]
	currPodPath = defaultPodDirPath

	podcastList = open(podcastListPath, 'r')
	nbPodUpdated = 0

	for line in podcastList:
		podcastUrl = line.decode('utf-8').strip(u'\n \t')
		m = p.match(podcastUrl)
		if m:
			gr = m.groups()
			podcastUrl = gr[1]
			regExpFilts = {}
			if gr[2]:
				for reg in subP.findall(gr[2]):
					regExpFilts[reg[0]] = reg[1:]
			if gr[0]:
				podcast = Podcast(podcastUrl, int(gr[0]), podcastDirPath = currPodPath)
			else:
				podcast = Podcast(podcastUrl, podcastDirPath = currPodPath)
			podcast.Save()
			podcast.UpdateTags(regExpFilts)
			nbPodUpdated += 1
			print(u"---------------------------------------------")
		else:
			currPodPath = podcastUrl + ('' if podcastUrl.endswith('/') else '/')
			if not os.path.isabs(currPodPath):
				raise ValueError(currPodPath + ' (in ' + podcastListPath + ') is not an absolute path.')
	podcastList.close()

	print(unicode(nbPodUpdated) + u' podcast' + (' has' if nbPodUpdated == 1 else 's have') +' been updated.')
	if nbPodUpdated == 0:
		print(podcastListPath + u" didn't contain any podcasts.")


if __name__ == '__main__':
    main()
