from logging import getLogger

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import SSLError

from pyDownloader.pyDownloader import DownloadState
from .exceptions import ProtocolNotConfiguredException
from .protocols import Protocols


class HTTPDownloader(Protocols):
    _logger = getLogger(__name__)

    def __init__(self, uri, local_path, **kwargs):
        # Set the local file path
        self.local_path = local_path

        # Split the URI properly based on if it is authenticated or no
        self.protocol = 'http'
        if '@' in str(uri).replace('http://', '') and ':' in str(uri).replace('http://', ''):
            self.username = str(uri).replace('http://', '').split('@')[0].split(':')[0]
            self.password = str(uri).replace('http://', '').split('@')[0].split(':')[1]
            self.host = str(uri).replace('http://', '').split('@')[1].split('/')[0]
            self.path = '/'.join(str(uri).replace('http://', '').split('/')[1:])

        elif '@' not in str(uri).replace('http://', '') and ':' not in str(uri).replace('http://', ''):
            self.username = None
            self.password = None
            self.host = str(uri).replace('http://', '').split('/')[0]
            self.path = '/'.join(str(uri).replace('http://', '').split('/')[1:])

        else:
            self.state = DownloadState.FAILED
            raise ProtocolNotConfiguredException('http')

    def _download(self, timeout=(60,)):
        self.remove_file()
        if not hasattr(self, 'ssl_verify'):
            self.ssl_verify = True

        try:
            self._logger.info('Downloading: http://' + self.host + '/' + self.path)
            if self.username is not None and self.password is not None:
                self._logger.debug('Authenticated HTTP Download')
                request = requests.get(url=self.protocol + '://' + self.host + '/' + self.path,
                                       stream=True,
                                       verify=self.ssl_verify,
                                       auth=HTTPBasicAuth(self.username, self.password),
                                       timeout=timeout)
            else:
                self._logger.debug('Un-Authenticated HTTP Download')
                request = requests.get(url=self.protocol + '://' + self.host + '/' + self.path, stream=True,
                                       verify=self.ssl_verify,
                                       timeout=timeout)
        except SSLError:
            self._logger.error("SSL Verification Failed!")
            self.state = DownloadState.FAILED
            return

        self._logger.debug('File Size: ' + request.headers['content-length'])

        self.file_size = int(request.headers['content-length'])
        self.downloaded_size = 0

        self._logger.debug('File Download starting')
        self.state = DownloadState.DOWNLOADING
        try:
            with open(self.local_path, 'wb') as f:
                for chunk in request.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        self.downloaded_size += 8192
        except:
            self.state = DownloadState.FAILED
            raise

        self.state = DownloadState.FINISHED
        self._logger.debug('Download finished')
