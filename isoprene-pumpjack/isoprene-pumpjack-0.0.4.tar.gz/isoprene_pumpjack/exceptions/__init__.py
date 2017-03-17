#!/usr/bin/env python
'''
Application exceptions
'''

class ServiceException(Exception):
    pass

class GraphServiceException(ServiceException):
    pass

class DocumentServiceException(ServiceException):
    pass
