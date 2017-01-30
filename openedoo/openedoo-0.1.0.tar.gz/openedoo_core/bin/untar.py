# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 06:59:20 2014
 
@author: Sukhbinder Singh
 
Tarfile test
 
"""

dir_path = os.path.dirname(__file__)

import tarfile

def untar(filename="openedoo.tar.gz"):
	tar = tarfile.open("{dir}/sample.tar.gz".format(dir=dir_path))
	tar.extractall()
	tar.close()
	return "file has installed"