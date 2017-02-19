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
import re, htmlentitydefs
import os
from tqdm import tqdm
import requests

def FetchFile(url, filePath):
	try:
		response = requests.get(url, stream=True)
		sz = response.headers.get('content-length')
		csz = 1024
		if sz is not None:
			sz = int(sz) / csz
		with open(filePath, "wb") as fileObj:
			for data in tqdm(response.iter_content(chunk_size=csz), total=sz, unit='kB'):
				fileObj.write(data)
	except IOError as ex:
		print(u"IO error saving " + url + u": " + unicode(ex))
		fileObj.close()
		os.remove(filePath)
		return False
	except Exception as ex:
		print(u"Error: " + unicode(ex) + u" did not fetch " + filePath)
		fileObj.close()
		os.remove(filePath)
		return False
	fileObj.close()
	return True
