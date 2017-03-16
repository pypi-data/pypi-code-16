import os
from queue import Queue
from threading import Thread

from PyQt5.QtGui import QPixmap
from requests import get

_Supported_Extensions = ['.jpeg', '.png', '.jpg', '.gif']


class ImageQueue():
    def __init__(self, src: str, dst: str):
        """
        通过queue预加载图片
        :param src: 图片来源
        """
        self.queue = Queue(3)
        self.dst = dst
        self.src = src
        self.load_from_url = src.startswith('http')
        if src.startswith('http'):
            self.total = 'Na'
        else:
            self.files = [f for f in os.listdir(src) if os.path.splitext(f)[1] in _Supported_Extensions]
            self.total = str(len(self.files))
        while not self.queue.full():
            self.queue.put(self._load())

    def save(self, name: str, img: QPixmap):
        """
        将识别结果保存到dst
        """
        abs_path = os.path.join(self.dst, name + '.png')
        img.save(abs_path)

    def get(self):
        if self.queue.empty():
            return None
        img = self.queue.get()
        Thread(target=lambda: self.queue.put(self._load())).start()
        return img

    def _load(self):
        if self.load_from_url:
            qp = QPixmap()
            qp.loadFromData(get(self.src).content)
            return qp
        else:
            if len(self.files) > 0:
                qp = QPixmap()
                file_path = os.path.join(self.src, self.files.pop(0))
                with open(file_path, 'rb') as fh:
                    qp.loadFromData(fh.read())
                return qp
                # return QPixmap(os.path.join(self.src, self.files.pop(0)))
