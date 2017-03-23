#!/usr/bin/env python
# encoding: utf-8

# Copyright (C) 2015 Chintalagiri Shashank
# Released under the MIT license.

"""
Sets up a :class:`twisted.web.resource.Resource` hierarchy containing the
filesystems to expose. The exposed filesystems are specified by
:data:`fs_server.config.FILESYSTEMS`, which you should set to what you need.

.. rubric:: Usage Example

>>> # See the config module for details for setting the filesystems.
>>> # After you do, start the service :
>>> from fs_server.config import SERVER_PORT
>>> from fs_server.serve import get_resource
>>> from twisted.internet import reactor
>>> from twisted.web.server import Site
>>> factory = Site(get_resource())
>>> reactor.listenTCP(SERVER_PORT, factory)
>>> reactor.run()

"""

from fs.opener import fsopendir
from fs.expose.xmlrpc import RPCFSInterface

from config import FILESYSTEMS
from config import SERVER_PORT

from twisted.web import xmlrpc
from twisted.web.resource import Resource
from twisted.web import server
from twisted.application import internet
from twisted.python import log


class XMLRPCFSEndpoint(xmlrpc.XMLRPC):
    """

    A :class:`twisted.web.xmlrpc.XMLRPC` (and subsequently,
    :class:`twisted.web.resource.Resource` subclass), defining the
    interface between :mod:`fs.expose.xmlrpc` with Twisted.

    """
    def __init__(self, fs):
        self._fs_if = RPCFSInterface(fs)
        xmlrpc.XMLRPC.__init__(self, allowNone=True)

        self._procedureToCallable = {
            'encode_path': self._fs_if.encode_path,
            'decode_path': self._fs_if.decode_path,
            'getmeta': self._fs_if.getmeta,
            'getmeta_default': self._fs_if.getmeta_default,
            'hasmeta': self._fs_if.hasmeta,
            'get_contents': self._fs_if.get_contents,
            'set_contents': self._fs_if.set_contents,
            'exists': self._fs_if.exists,
            'isdir': self._fs_if.isdir,
            'isfile': self._fs_if.isfile,
            'listdir': self._fs_if.listdir,
            'makedir': self._fs_if.makedir,
            'remove': self._fs_if.remove,
            'removedir': self._fs_if.removedir,
            'rename': self._fs_if.rename,
            'settimes': self._fs_if.settimes,
            'getinfo': self._fs_if.getinfo,
            'desc': self._fs_if.desc,
            'getxattr': self._fs_if.getxattr,
            'setxattr': self._fs_if.setxattr,
            'delxattr': self._fs_if.delxattr,
            'listxattrs': self._fs_if.listxattrs,
            'copy': self._fs_if.copy,
            'move': self._fs_if.move,
            'movedir': self._fs_if.movedir,
            'copydir': self._fs_if.copydir,
        }

    def lookupProcedure(self, procedure_path):
        """
        Overrides :func:`twisted.web.xmlrpc.XMLRPC.lookupProcedure`, changing
        it's behavior from teh default of looking for ``xmlrpc_`` functions to
        using the :data:`_procedureToCallable` dictionary instead.
        """
        try:
            return self._procedureToCallable[procedure_path]
        except KeyError:
            raise xmlrpc.NoSuchFunction(
                self.NOT_FOUND, "procedure %s not found" % procedure_path
            )

    def listProcedures(self):
        """
        Returns the list of supported procedures.
        """
        return self._procedureToCallable.keys()


class FSServer(object):
    """
    The XML-RPC resource tree, created on top of the provided ``root``. If
    no root is provided, one is created (returned by :func:`setup()`).
    """
    def __init__(self, root=None):
        log.msg("Initializing fs_server Resource")
        self._filesystems = FILESYSTEMS
        self._endpoints = self._wrap_filesystems()
        self._root = root

    def _wrap_filesystems(self):
        """
        Wraps the filesystems with :class:`XMLRPCFSEndpoint`, creating the
        various instances as a list containing tuples of the resource name
        (obtained from the config) and the Resource instance.
        """
        rval = []
        for filesystem in self._filesystems:
            log.msg("Wrapping filesystem : {0}".format(filesystem[0]))
            rval.append(
                (filesystem[0], XMLRPCFSEndpoint(fsopendir(filesystem[1])))
            )
        return rval

    def setup(self):
        """
        Creates the actual resource tree, attaching the various
        filesystems to the provided root.

        :returns: the Root of the Resource tree
        """
        if not self._root:
            log.msg("Creating Site Root")
            self._root = Resource()
        for endpoint in self._endpoints:
            log.msg("Adding XML-RPC Resource : " + endpoint[0])
            self._root.putChild(*endpoint)
        return self._root


def get_resource(root=None):
    """
    Created and returns the resource tree containing the various
    XML-RPC FS resources.

    :param root: Root on which the resource tree should be built.
    :return: The root on which the resource tree was built.
    """
    xmlrp_server = FSServer(root)
    root = xmlrp_server.setup()
    return root


def get_service():
    """
    Return a service containing the resource suitable for creating
    an application object.
    """
    root = get_resource()
    xmlrpc_factory = server.Site(root)
    return internet.TCPServer(SERVER_PORT, xmlrpc_factory)
