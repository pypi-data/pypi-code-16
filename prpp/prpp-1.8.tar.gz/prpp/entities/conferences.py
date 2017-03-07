'''
Created on 5 févr. 2016

@author: Adrien
'''
from ..wrapper.request import PRPPRequest

class Conferences(PRPPRequest):
    
    def __init__(self, server, path="conferences"):
        super(Conferences,self).__init__(server, path)
