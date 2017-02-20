from threading import Thread

from webcam.services.opencv import OpenCV


class VideoStream:
    def __init__(self):
        self.cv = OpenCV()
        self.stream = self.cv.get_capture()

        self.current_frame = None
        self.is_reading = True

    def is_open(self):
        return self.stream.isOpened()

    def start(self):
        self.is_reading = True
        self.stream.set(3, 1280)
        self.stream.set(4, 720)
        Thread(target=self.__start_reading_frames).start()

    def stop(self):
        self.is_reading = False

    def release(self):
        self.cv.release()

    def read(self):
        frame = self.current_frame
        self.current_frame = None
        return frame

    def __start_reading_frames(self):
        while True:
            if self.is_reading is False:
                return
            _grabbed, self.current_frame = self.stream.read()
