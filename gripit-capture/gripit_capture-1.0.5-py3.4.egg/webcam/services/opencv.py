import cv2


class OpenCV:
    def __init__(self):
        self.capture = None

    def get_capture(self):
        if not self.capture:
            self.capture = cv2.VideoCapture(0)
        return self.capture

    def release(self):
        self.capture.release()
        self.capture = None
