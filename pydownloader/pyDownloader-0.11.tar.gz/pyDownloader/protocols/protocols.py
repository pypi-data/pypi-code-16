from abc import ABCMeta, abstractmethod
from .exceptions import ProtocolNotConfiguredException
import _thread


class Protocols(object, metaclass=ABCMeta):
    error = False
    downloading = False
    file_size = 0
    downloaded_size = 0

    @abstractmethod
    def __init__(self, uri, local_path, **kwargs):
        raise ProtocolNotConfiguredException(__name__)

    def download_async(self, timeout=(60,)):
        if not self.downloading:
            _thread.start_new(self._download, timeout)

    def download(self, timeout=(60,)):
        self.download_async(timeout)

        while not self.completed():
            pass

    def get_progress(self):
        if self.downloading:
            return self.downloaded_size * 100 // self.file_size
        else:
            return 0

    def completed(self):
        if self.get_progress() >= 100:
            print("Completed!")
            return True
        else:
            return False

    @abstractmethod
    def _download(self):
        pass
