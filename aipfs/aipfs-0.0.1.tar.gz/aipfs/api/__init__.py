import asyncio

from aipfs.transport import AsyncHTTP
from .bitswap import Bitswap
from .block import Block
from .bootstrap import Bootstrap
from .config import Config
from .dht import DHT
from .diag import Diag
from .file import File
from .files import Files
from .ipfsobject import Object as _Object
from .log import Log
from .name import Name
from .pin import Pin
from .refs import Refs
from .repo import Repo
from .stats import Stats
from .swarm import Swarm
from .tar import Tar


class IPFS(object):

    """IPFS api"""

    def __init__(self, loop=None, endpoint="http://localhost:5001/api/v0", transport=AsyncHTTP):

        # get event loop
        self.loop = loop or asyncio.get_event_loop()

        # instance transport
        self.transport = transport(loop=self.loop, base_url=endpoint)

        self.name = Name(self.transport)

        self.pin = Pin(self.transport)

        self.refs = Refs(self.transport)

        self.repo = Repo(self.transport)

        self.stats = Stats(self.transport)

        self.swarm = Swarm(self.transport)

        self.tar = Tar(self.transport)

        self.bitswap = Bitswap(self.transport)

        self.block = Block(self.transport)

        self.bootstrap = Bootstrap(self.transport)

        self.config = Config(self.transport)

        self.dht = DHT(self.transport)

        self.diag = Diag(self.transport)

        self.file = File(self.transport)

        self.files = Files(self.transport)

        self.log = Log(self.transport)

        self.object = _Object(self.transport)

    @asyncio.coroutine
    def add(self, filestream, **kwargs):
        """Add a file to ipfs

        :param filestream: Stream file to be added to IPFS.
        :type filestream: io.IOBase

        :return:  dict -- return code.
           ::

              {
                 "Name": "<string>",
                 "Hash": "<string>",
                 "Bytes": "<int64>"
              }
        """
        data = {
            "file": filestream
        }

        params = {
            "recursive": kwargs.get("recursive", False),
            "quiet": kwargs.get("quiet", False),
            "silent": kwargs.get("silent", False),
            "progress": kwargs.get("progrees", False),
            "trickle": kwargs.get("trickle", False),
            "only_hash": kwargs.get("only_hash", False),
            "wrap_with_directory": kwargs.get("wrap_with_directory", False),
            "hidden": kwargs.get("hidden", False),
            "chunker": kwargs.get("chunker", None),
            "pin": kwargs.get("pin", True)
        }

        res = yield from self.transport.request('post', endpoint="/add", data=data, params=params)
        return (yield from res.json())

    @asyncio.coroutine
    def cat(self, path):
        """Show IPFS object data

        :param path: ipfs path object
        :type path: str

        :return: bytes -- file
        """
        res = yield from self.transport.request('get', endpoint="/cat", params={"arg": path})
        return (yield from res.read())

    @asyncio.coroutine
    def dns(self, domain_name, recursive=False):
        """DNS link resolver

        :param domain_name: domain-name name to resolve
        :type domain_name: str

        :param recursive: Resolve until the result is not a DNS link. Default: False
        :type recursive: bool

        :return: dict -- return.
           ::

              {
                 "Path": "<string>"
              }
        """
        params = {
            "arg": domain_name,
            "recursive": recursive
        }
        res = yield from self.transport.request('get', endpoint="/dns", params=params)
        return (yield from res.json)

    @asyncio.coroutine
    def get(self, path, **kwargs):
        """Download IPFS objects.

        :param path: path IPFS object
        :type path: str

        :return: bytes -- file body
        """
        params = {
            "arg": path,
            "output": kwargs.get("output", None),
            "archive": kwargs.get("archive", False),
            "compress": kwargs.get("compress", False),
            "compression-level": kwargs.get("compression_level", -1)
        }
        res = yield from self.transport.request('get', endpoint="/get", params=params)
        return (yield from res.read())

    @asyncio.coroutine
    def id(self, peer_id="", _format=""):
        """Show IPFS Node ID info.

        :param peer_id: Peer.ID of node to look up.
        :type peer_id: str

        :param _format: Optional output format
        :type _format: str

        :return: dict -- return
           ::

              {
                 "ID": "<string>",
                 "PublicKey": "<string>",
                 "Addresses": [
                    "<string>"
                 ],
                 "AgentVersion": "<string>",
                 "ProtocolVersion": "<string>"
              }
        """
        params = {
            "arg": peer_id,
            "format": _format
        }
        res = yield from self.transport.request('get', endpoint="/id", params=params)
        return (yield from res.json())

    @asyncio.coroutine
    def ls(self, path, headers=False, resolve_type=True):
        """List links from an objects.

        :param path: The path to the IPFS object(s) to list links from
        :type path: str

        :param headers: Print table headers (Hash, Size, Name). Default: False
        :type headers: bool

        :param resolve_type: Resolve linked objects to find out their types. Default: True
        :type resolve_type: bool

        :return: dict -- return
           ::

              {
                 "Objects": [
                    {
                       "Hash": "<string>",
                       "Links": [
                          {
                             "Name": "<string>",
                             "Hash": "<string>",
                             "Size": "<uint64>",
                             "Type": "<int32>"
                          }
                       ]
                    }
                 ]
              }
        """
        params = {
            "arg": path,
            "headers": headers,
            "resolve-type": resolve_type
        }
        res = yield from self.transport.request('get', endpoint="/ls", params=params)
        return (yield from res.json())

    @asyncio.coroutine
    def mount(self, ipfs_path=None, ipns_path=None):
        """Mounts IPFS to the filesystem (read-only).

        :param ipfs_path: The path where IPFS should be mounted.
        :type ipfs_path: str

        :param ipns_path: The path where IPNS should be mounted.
        :type ipns_path: str

        :return: dict -- return code
           ::

              {
                 "IPFS": "<string>",
                 "IPNS": "<string>",
                 "FuseAllowOther": "<bool>"
              }
        """
        params = {
            "ipfs-path": ipfs_path,
            "ipns-path": ipns_path
        }
        res = yield from self.transport.request('get', endpoint="/mount", params=params)
        return (yield from res.json())

    @asyncio.coroutine
    def ping(self, peer_id, count=10):
        """Send echo request packets to IPFS hosts.

        :param peer_id: ID of peer to be pinged
        :type peer_id: str

        :param count: Number of ping messages to send. Default: 10
        :type count: int

        :return: dict -- return
           ::

              {
                 "Success": "<bool>",
                 "Time": "<int64>",
                 "Text": "<string>"
              }
        """
        params = {
            'arg': peer_id,
            'count': count
        }
        res = yield from self.transport.request('get', endpoint='/ping', params=params)
        return (yield from res.json())

    @asyncio.coroutine
    def resolve(self, ipfsname, recursive=False):
        """Resolve the value of names to IPFS.

        :param ipfsname: The name to resolve.
        :type ipfsname: str

        :param recursive: Resolve until the result is an IPFS name. Default: False
        :type recursive: bool

        :return: dict -- return
           ::

              {
                 "Path": "<string>"
              }
        """
        params = {
            'arg': ipfsname,
            'recursive': recursive
        }
        res = yield from self.transport.request('get', endpoint='/resolve', params=params)
        return (yield from res.json())

    @asyncio.coroutine
    def version(self):
        """Shows ipfs version information.

        :return: dict -- return
           ::

              {
                 "Version": "<string>",
                 "Commit": "<string>",
                 "Repo": "<string>",
                 "System": "<string>",
                 "Golang": "<string>"
              }
        """
        return (yield from self.transport.request('get', endpoint="/version"))

    def close(self):
        """Close all transport"""
        self.transport.close()

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()
