class Files(object):

    base_endpoint = '/files'

    def __init__(self, transport):
        self.transport = transport

    def cp(self, source, dest):
        """Copy files into mfs.
        :param source: Source object to copy.
        :type source: str

        :param dest: Destination to copy object to.
        :type dest: str

        :return: bytes -- file
        """
        endpoint = self.base_endpoint + '/cp'
        params = [("arg", source), ("arg", dest)]
        res = yield from self.transport.request('get', endpoint=endpoint, params=params)
        return (yield from res.read())

    def flush(self, path="/"):
        """Flush a given path's data to disk.

        :param path: Path to flush. Default: '/'.
        :type path: str

        :return: bytes -- file
        """
        endpoint = self.base_endpoint + '/flush'
        params = {
            'arg': path
        }
        res = yield from self.transport.request('get', endpoint=endpoint, params=params)
        return (yield from res.read())

    def ls(self, path='/', long=False):
        """List directories.

        :param path: Path to show listing for. Defaults to '/'.
        :type path: str

        :param long: Use long listing format
        :type long: bool

        :return: dict -- return
           ::

              {
                 "Entries": [
                    {
                       "Name": "<string>",
                       "Type": "<int>",
                       "Size": "<int64>",
                       "Hash": "<string>"
                    }
                 ]
              }

        """
        endpoint = self.base_endpoint + '/ls'
        params = {
            'arg': path,
            'l': long
        }
        res = yield from self.transport.request('get', endpoint=endpoint, params=params)
        return (yield from res.json())

    def mkdir(self, path, parent=False):
        """Make directories.

        :param path: Path to dir to make
        :type path: str

        :param parent: No error if existing, make parent directories as needed.
        :type parent: bool

        :return: bytes -- file
        """
        endpoint = self.base_endpoint + '/mkdir'
        params = {
            'arg': path,
            'parent': parent
        }
        res = yield from self.transport.request('get', endpoint=endpoint, params=params)
        return (yield from res.read())

    def mv(self, source, dest):
        """Move files.

        :param source: Source file to move.
        :type source: str

        :param dest: Destination path for file to be moved to.
        :type dest: str

        :return: bytes -- file
        """
        endpoint = self.base_endpoint + '/mv'
        params = [('arg', source), ('arg', dest)]
        res = yield from self.transport.request('get', endpoint=endpoint, params=params)
        return (yield from res.read())

    def read(self, path, offset=None, count=None):
        """Read a file in a given mfs.

        :param path: Path to file to be read.
        :type path: str

        :param offset: Byte offset to begin reading from.
        :type offset: int

        :param count: Maximum number of bytes to read.
        :type count: int

        :return: bytes -- file
        """
        endpoint = self.base_endpoint + '/read'
        params = {
            'arg': path,
            'offset': offset,
            'count': count
        }
        res = yield from self.transport.request('get', endpoint=endpoint, params=params)
        return (yield from res.read())

    def rm(self, path, recursive=False):
        """Remove a file.

        :param path: File to remove.
        :type path: str

        :param recursive: Recursively remove directories.
        :type recursive: bool

        :return: bytes -- file
        """
        endpoint = self.base_endpoint + '/rm'
        params = {
            'arg': path,
            'recursive': recursive
        }
        res = yield from self.transport.request('get', endpoint=endpoint, params=params)
        return (yield from res.read())

    def stat(self, path, _hash=False, size=False):
        """Display file status.

        :param path: Path to node to stat.
        :type path: str

        :param _hash: Print only hash. Implies '--format='.
        :type _hash: bool

        :param size: Print only size.
        :type size: bool

        :return: dict -- return
           ::

              {
                 "Hash": "<string>",
                 "Size": "<uint64>",
                 "CumulativeSize": "<uint64>",
                 "Blocks": "<int>",
                 "Type": "<string>"
              }

        """
        endpoint = self.base_endpoint + '/stat'
        params = {
            'arg': path,
            'hash': _hash,
            'size': size
        }
        res = yield from self.transport.request('get', endpoint=endpoint, params=params)
        return (yield from res.json())

    def write(self, path, filestream, offset=None, create=False, truncate=False, count=None):
        """Write to a mutable file in a given filesystem.

        :param path: Path to write to.
        :type path: str

        :param filestream: Data to write.
        :type filestream: io.BaseStream

        :param offset: Byte offset to begin writing at.
        :type offset: int

        :param create: Create the file if it does not exist.
        :type create: bool

        :param truncate: Truncate the file to size zero before writing.
        :type truncate: bool

        :param count: Maximum number of bytes to read.
        :type count: int

        :return: bytes -- file
        """
        endpoint = self.base_endpoint + '/write'
        params = {
            'arg': path,
            'offset': offset,
            'create': create,
            'truncate': truncate,
            'count': count
        }
        data = {
            'file': filestream
        }
        res = yield from self.transport.request('post', endpoint=endpoint, data=data, params=params)
        return (yield from res.read())
