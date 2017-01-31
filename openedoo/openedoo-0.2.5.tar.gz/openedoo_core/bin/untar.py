# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 06:59:20 2014
 
@author: Sukhbinder Singh
 
Tarfile test
 
"""
import os
import tarfile

dir_path = os.path.dirname(__file__)

def untar_file(filename="openedoo.tar.gz"):
	tar = tarfile.open("{dir}/{name}".format(dir=dir_path,name=filename))
	tar.extractall()
	tar.close()
	return "file has installed"