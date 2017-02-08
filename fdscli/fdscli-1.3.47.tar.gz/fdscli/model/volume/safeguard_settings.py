# Copyright (c) 2016, Formation Data Systems, Inc. All Rights Reserved.
#
'''
Created on Dec 28, 2016

@author: nate
'''

class SafeGuardSettings(object):
    '''
    Bean object that contains safeguard information for the volume
    
    Instead of just putting this in the volume it is separate for ease
    of extension properties that may one day exist in this structure
    '''


    def __init__(self, safeguard_type=None):
        
        self.safeguard_type = safeguard_type
        
    @property
    def safeguard_type(self):
        return self.__safeguard_type
    
    @safeguard_type.setter
    def safeguard_type(self, a_type):
        self.__safeguard_type = a_type