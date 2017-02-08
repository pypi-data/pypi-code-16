import os
from logging import getLogger
from .protocols import Protocols
from .exceptions import ProtocolNotConfiguredException
from ftplib import FTP
from urllib.parse import urlparse


class FTPDownloader(Protocols):
    _logger = getLogger(__name__)

    connection = None

    def __init__(self, uri, local_path, **kwargs):
        # Set the local file path
        self.local_path = local_path
        self._logger.debug('Local Path: ' + self.local_path)

        # Split the URI properly based on if it is authenticated or no
        self._logger.debug('URI: ' + uri)
        parsed_url = urlparse(uri)

        # Set the port (Default to 21)
        if 'port' in kwargs:
            self.port = kwargs['port']
        else:
            try:
                self.port = parsed_url.port
            except ValueError as e:
                self._logger.error("URL Malformed. Port is not an integer or none.")
                raise ProtocolNotConfiguredException('ftp') from e
            if self.port is None:
                self.port = 21

        self._logger.debug('Port: ' + str(self.port))

        if parsed_url.scheme != 'ftp':
            self._logger.debug('Scheme: ' + parsed_url.scheme)
            raise ProtocolNotConfiguredException('ftp')

        self.protocol = parsed_url.scheme
        self.connection = FTP()

        if 'username' in kwargs:
            self.username = kwargs['username']
        else:
            self.username = parsed_url.username

        if 'password' in kwargs:
            self.password = kwargs['password']
        else:
            self.password = parsed_url.password

        self.host = parsed_url.hostname
        self.path = parsed_url.path

        self._logger.debug('Username: ' + str(self.username))
        self._logger.debug('Password: ' + str(self.password))
        self._logger.debug('Hostname: ' + self.host)
        self._logger.debug('Path    : ' + self.path)

    def _download(self, timeout=(60,)):
        try:
            self._logger.debug('Removing file!')
            os.remove(self.local_path)
        except OSError:
            self._logger.debug('File can\'t be overwritten!')
            if os.path.isfile(self.local_path):
                self._logger.debug('File still exists!')
                return
            else:
                self._logger.debug('File doesn\'t exist!')
                pass
        self.connection.timeout = timeout
        self.connection.connect(host=self.host, port=self.port)
        self._logger.debug('FTP Connection open')

        if self.username is not None:
            self.connection.login(user=self.username, passwd=self.password)
            self._logger.debug('FTP Connection authenticated')
        else:
            self.connection.login()

        self.file_size = self.connection.size(self.path)
        self.downloading = True
        self.connection.retrbinary('RETR ' + self.path, self.writeBlock, blocksize=1024)

        self._logger.debug('File Written!')

    def writeBlock(self, data_block):
        with open(self.local_path, 'ab') as f:
            f.write(data_block)
            self.downloaded_size += 1024
