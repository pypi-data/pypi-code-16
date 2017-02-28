'''Nodes provides the methods for chef node resources'''

from .base import Base


class Nodes(Base):
    '''
    Provides access to the chef nodes
    '''
    _base_url = '/organizations/%(org)s/nodes'

    @classmethod
    def exists(cls, nodename):
        '''
        Checks if a node exists on the chef server

        :param username: The Node's nodename
        :type usename: string
        :return: If the node exists
        :rtype: boolean
        '''
        return super(Nodes, cls).exists(nodename)
