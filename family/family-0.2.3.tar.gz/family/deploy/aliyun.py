# coding-utf8



'''
usage:

    * add slb listener
    * create and sync supervisor config
    * operate supervisor: reread, update, start, stop, restart, etc
'''


from aliyunsdkcore import client
from aliyunsdkslb.request.v20160520 import DescribeHealthStatusRequest
from aliyunsdkslb.request.v20160520 import CreateLoadBalancerHTTPListenerRequest
from aliyunsdkslb.request.v20160520 import StartLoadBalancerListenerRequest



class Listener(object):

    def __init__(self, access_id, access_secret, region):
        self.client = client.AcsClient(access_id, access_secret, region)

    def add_listener(self, slb, port):
        request = CreateLoadBalancerHTTPListenerRequest.CreateLoadBalancerHTTPListenerRequest()
        request.set_LoadBalancerId(slb)
        request.set_ListenerPort(port)
        request.set_BackendServerPort(port)
        request.set_Bandwidth(-1)
        request.set_StickySession('off')
        request.set_HealthCheck('off')
        return self.client.do_action(request)


    def start_listener(self, slb, port):
        request = StartLoadBalancerListenerRequest.StartLoadBalancerListenerRequest()
        request.set_LoadBalancerId(slb)
        request.set_ListenerPort(port)
        return self.client.do_action(request)
