description = "a module housing useful functions for the heartbeat monitoring of lvalert_listenMP processes"
author = "Reed Essick (reed.essick@ligo.org)"

#-------------------------------------------------

import os

from numpy import infty
import lvalert_heartbeat

from lvalertMP.lvalert import lvalertMPutils

#-------------------------------------------------

class HeartbeatItem(lvalertMPutils.QueueItem):
    '''
    a wrapper around heartbeat functionality for lvalertMP
    '''
    name = 'heartbeat'
    description = 'a response to heartbeat queries'

    def __init__(self, t0, name, alert, netrc=os.getenv('NETRC', os.path.join(os.path.expanduser('~'), '.netrc')), logTag='iQ'):
        tasks = [HeartbeatTask(name, alert, netrc=netrc, logTag=logTag)]
        super(HeartbeatItem, self).__init__(t0, tasks, logTag=logTag)

class HeartbeatTask(lvalertMPutils.Task):
    '''
    a wrapper around heartbeat functionality for lvalertMP
    '''
    name = 'heartbeat'
    description = 'a response to heartbeat queries'

    def __init__(self, process_name, alert, netrc=os.getenv('NETRC', os.path.join(os.path.expanduser('~'), '.netrc')), logTag='iQ'):
        self.process_name = process_name
        self.alert = alert
        self.netrc = netrc
        super(HeartbeatTask, self).__init__(-infty, logTag=logTag) ### do this immediately, always
        print self.logTag

    def heartbeat(self, verbose=False):
        '''
        delegate to a helper function
        '''
        lvalert_heartbeat.respond( self.process_name, self.alert, netrc=self.netrc, verbose=verbose, logTag=self.logTag )

#-------------------------------------------------

def parseHeartbeat( queue, queueByGraceID, alert, t0, config, logTag='iQ' ):
    '''
    a function that parses alerts specifically for heartbeat packets.
    should be called within parse_alert as needed
    '''
    assert alert['uid']=='heartbeat', 'I only know how to parse alerts with uid="heartbeat"'
    queue.insert( HeartbeatItem( t0, config.get('data','name'), alert, netrc=config.get('data', 'netrc'), logTag=logTag) )
    return 0
