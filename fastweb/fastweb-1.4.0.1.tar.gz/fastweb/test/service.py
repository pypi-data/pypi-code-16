# coding:utf8


import unittest

from fastweb.service import MicroService


class HelloServiceHandler:

    def sayHello(self):
        print 'sayHello'


class ServiceTest(unittest.TestCase):

    def runTest(self):
        service = MicroService('test', thrift_module='gen-py.HelloService.HelloService', handler=HelloServiceHandler)
        service.start(port=9999)


if __name__ == '__main__':
    unittest.main()
