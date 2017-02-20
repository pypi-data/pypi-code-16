from collections import namedtuple
from datetime import datetime

CAPTURE_EXECUTABLE = 'ov2640_capture'
X_RESOLUTION = 800
Y_RESOLUTION = 600

CameraCaptureResult = namedtuple(
    'CameraCaptureResult',
    'filename'
)

class Camera:
    def capture(self, filename=None):
        print("<[VIRTUAL MACHINE LOG] - Picture taken>")
