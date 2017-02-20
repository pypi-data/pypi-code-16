from threading import Thread

import cv2

from webcam.config import Config


class File:
    def __init__(self):
        self.video_writer = None
        self.current_file = None
        self.last_file = None

    def write(self, frames):
        if self.__file_is_open:
            Thread(target=self.__write_frames, args=(frames,)).start()

    def release(self):
        if self.__file_is_open:
            self.video_writer.release()

    def create(self, name):
        self.__set_last_file(name)
        self.current_file = name
        self.video_writer = self.__video_writer(name)

    def last(self):
        return self.last_file

    def current(self):
        return self.current_file

    def __write_frames(self, frames):
        for frame in frames:
            self.video_writer.write(frame)
        self.release()

    def __video_writer(self, file_name):
        return cv2.VideoWriter(file_name + Config.OUTPUT_FILE_EXTENSION,
                                   self.__video_codec(),
                                   Config.VIDEO_FPS,
                                   Config.VIDEO_RESOLUTION)

    def __set_last_file(self, name):
        self.last_file = self.current_file if self.current_file is not None else name

    def __file_is_open(self):
        return self.video_writer.isOpened()

    def __video_codec(self):
        return cv2.VideoWriter_fourcc(*Config.VIDEO_CODEC)
