
# -*- coding:utf-8 -*-

from ..util import client, result_cache,config
from terminal import confirm,green


def update(clusterId, nodes, groupName='group', yes=False):
    v = int(nodes)

    if v < 0:
        raise Exception('Invalid nodes')


    clusterId = result_cache.get(clusterId, 'clusters', True)
    groupName = result_cache.get(groupName, 'groups')


    if yes:
        client.change_cluster_vmcount(clusterId, groupName, nodes)
        print(green('done'))
    else:
        if confirm('Change desiredVMCount of %s.%s' % (clusterId, groupName), default=False):
            client.change_cluster_vmcount(clusterId, groupName, nodes)
            print(green('done'))
