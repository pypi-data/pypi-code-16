import time
import logging

logger = logging.getLogger(__name__)


class Faas(object):
    """
    Wrapper to the ldap lib, one that will make you happy.

    ldap docs: https://www.python-ldap.org/doc/html/ldap.html
    ldap docs references: https://www.python-ldap.org/docs.html
    ldap samples: http://www.grotan.com/ldap/python-ldap-samples.html
    """

    def __init__(self):
        pass

    def say_hey(self):
        print "hey"
