from threading import Thread

import time

from webcam.config import Config

from webcam.data.file import File
from webcam.data.stream_buffer import StreamBuffer
from webcam.jobs.converting_job import ConvertingJob
from webcam.services.video_stream import VideoStream

from imutils.video import FPS


class Camera:
    def __init__(self):
        self.stream = VideoStream()

        self.file = File()
        self.converting_job = ConvertingJob()

        self.is_recording = False
        self.is_camera_open = False

        self.buffer = StreamBuffer()
        self.file_name = None

        self.fps = FPS()


    def is_open(self):
        return self.is_camera_open

    def access(self):
        self.is_camera_open = True
        Thread(target=self.__start_reading_frames).start()

    def release(self):
        self.is_camera_open = False
        # self.stream.release()

    def start_recording(self):
        if self.is_open():
            print("Start RECORDING Video")
            self.fps.start()
            self.stream.start()
            self.is_recording = True

    def stop_recording(self):
        print("Stop RECORDING Video")
        self.is_recording = False
        self.stream.stop()

        self.fps.stop()
        print("[INFO] elasped time: {:.2f}".format(self.fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(self.fps.fps()))

        Config.VIDEO_FPS = self.fps.fps()
        self.file.create(self.file_name)
        self.__write_frames()

        # last_file = self.file.last()
        # self.converting_job.convert(last_file)

    def create_file(self, name):
        # self.file.create(name)
        self.file_name = name

    def __start_reading_frames(self):
        print("Start READING frames")
        while self.stream.is_open() and self.is_open():
            if self.is_recording:
                frame = self.stream.read()
                if frame is not None:
                    self.buffer.insert(frame)
                    self.fps.update()

    def __write_frames(self):
        frames = self.buffer.get()
        self.file.write(frames)
