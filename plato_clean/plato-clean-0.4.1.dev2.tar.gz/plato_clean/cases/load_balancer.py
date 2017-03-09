from plato_clean.cases import get_resource
from plato_clean.cases import post_resource
from plato_clean.cases import wait_busy_resource


class CleanLoadBalancers(object):

    def run(self, API, sleep):
        # we can delete active, error load balancers.
        load_balancers = get_resource(API, 'DescribeLoadBalancers', {
            'status': ['active', 'error']
        }, 'loadBalancerSet')
        load_balancer_ids = [lb['loadBalancerId'] for lb in load_balancers]

        # get the listeners whos parents (load balancers) are active or error
        listeners = get_resource(API, 'DescribeLoadBalancerListeners', {
            'status': ['active', 'error'],
            'loadBalancerIds': load_balancer_ids,
        }, 'listenerSet')
        listener_ids = [l['loadBalancerListenerId'] for l in listeners]
        listener_related_lb_ids = [l['loadBalancerId'] for l in listeners]

        # get the backends whos parents (load balancers) are active or error
        backends = get_resource(API, 'DescribeLoadBalancerBackends', {
            'status': ['active'],
            'loadBalancerListenerIds': listener_ids
        }, 'backendSet')
        backend_ids = [b['loadBalancerBackendId'] for b in backends]
        backend_related_lb_ids = [b['loadBalancerId'] for b in backends]

        # step1: clean backends
        post_resource(API,
                      'DeleteLoadBalancerBackends',
                      backend_ids,
                      'loadBalancerBackendIds')
        # step1.1: wait lb.
        wait_busy_resource(API, 'DescribeLoadBalancers', {
            'loadBalancerIds': backend_related_lb_ids,
            'status': ['building']
        }, sleep)

        # step2: clean listeners
        post_resource(API,
                      'DeleteLoadBalancerListeners',
                      listener_ids,
                      'loadBalancerListenerIds')
        # step2.1 wait lb.
        wait_busy_resource(API, 'DescribeLoadBalancers', {
            'loadBalancerIds': listener_related_lb_ids,
            'status': ['building']
        }, sleep)

        # step3: clean load_balancers
        post_resource(API,
                      'DeleteLoadBalancers',
                      load_balancer_ids,
                      'loadBalancerIds')

        # raise exception for not deleted load balancers
        load_balancers = get_resource(API, 'DescribeLoadBalancers', {
            'status': ['active', 'error', 'pending', 'building']
        }, 'loadBalancerSet')
        load_balancer_ids = [lb['loadBalancerId'] for lb in load_balancers]

        listeners = get_resource(API, 'DescribeLoadBalancerListeners', {
            'status': ['active', 'error', 'pending', 'building']
        }, 'listenerSet')
        listener_ids = [lb['listenerId'] for lb in listeners]

        backends = get_resource(API, 'DescribeLoadBalancerBackends', {
            'status': ['active']
        }, 'backendSet')
        backend_ids = [b['loadBalancerBackendId'] for b in backends]

        if load_balancer_ids or listener_ids or backend_ids:
            msg = []
            if load_balancer_ids:
                msg.append('Cannot clean load balancers: %s' %
                           load_balancer_ids)
            if listener_ids:
                msg.append('Cannot clean load balancer '
                           'listeners: %s' % listener_ids)
            if backend_ids:
                msg.append('Cannot clean load balancers '
                           'backends: %s' % backend_ids)
            raise Exception('\n'.join(msg))
