import _thread
import os
import time
from abc import ABCMeta, abstractmethod

from pyDownloader.pyDownloader import DownloadState
from .exceptions import ProtocolNotConfiguredException


class Protocols(object, metaclass=ABCMeta):
    error = False
    error_message = ''
    state = DownloadState.NOT_STARTED
    file_size = 0
    downloaded_size = 0

    @abstractmethod
    def __init__(self, uri, local_path, **kwargs):
        raise ProtocolNotConfiguredException(__name__)

    def download_async(self, timeout=(60,)):
        if self.state == DownloadState.NOT_STARTED:
            _thread.start_new(self._download, timeout)

    def download(self, timeout=(60,)):
        self.download_async(timeout)
        while self.state is not DownloadState.FINISHED and self.state is not DownloadState.FAILED:
            if self.state is not DownloadState.DOWNLOADING:
                self._logger.debug('State: ' + str(self.state))
            else:
                self._logger.debug('Downloaded: ' + str(self.get_progress()) + '%')
            time.sleep(5)

    def remove_file(self):
        try:
            self._logger.debug('Removing file!')
            os.remove(self.local_path)
        except OSError:
            self.error_message = 'File can\'t be overwritten!'
            self._logger.debug(self.error_message)
            if os.path.isfile(self.local_path):
                self._logger.debug('File still exists!')
                self.state = DownloadState.FAILED
                raise
            else:
                self._logger.debug('File doesn\'t exist!')
                pass

    def get_progress(self):
        if self.state == DownloadState.DOWNLOADING:
            return self.downloaded_size * 100 // self.file_size
        elif self.state == DownloadState.NOT_STARTED:
            return 0
        elif self.state == DownloadState.FINISHED:
            return 100
        else:
            return -1

    def completed(self):
        if self.state is DownloadState.FINISHED:
            self._logger.debug('Finished Downloading.')
            return True
        else:
            return False

    @abstractmethod
    def _download(self):
        pass
