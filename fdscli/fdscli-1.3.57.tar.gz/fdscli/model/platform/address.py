# Copyright (c) 2015, Formation Data Systems, Inc. All Rights Reserved.
#
class Address(object):
    '''
    Created on Jun 5, 2015
    
    @author: nate
    '''
    def __init__(self, ipv4address=None, ipv6address=None):
        self.ipv4address = ipv4address
        if self.ipv4address is None:
            self.ipv4address = "127.0.0.1"
        self.ipv6address = ipv6address

    @property
    def ipv4address(self):
        return self.__ipv4address;

    @ipv4address.setter
    def ipv4address(self, ipv4address):
        self.__ipv4address = ipv4address

    @property
    def ipv6address(self):
        return self.__ipv6address

    @ipv6address.setter
    def ipv6address(self, ipv6address):
        self.__ipv6address = ipv6address
