import datetime
from kervi.camera import FrameCamera
from PIL import Image, ImageDraw
import io
import time
import picamera

class Cam_1(FrameCamera):
    def __init__(self):
        FrameCamera.__init__(self, "cam1", "Camera 1")
        self.font = self.get_font()
        self.fps = 10
        self.link_to_dashboard("system", "cam")

    def capture_frames(self):
        with picamera.PiCamera() as camera:
            camera.resolution = (self.width, self.height)
            camera.framerate = self.fps
            time.sleep(2)
            stream = io.BytesIO()
            for foo in camera.capture_continous(stream, format="jpeg", use_video_port=True):
                stream.seek(0)
                image = Image.open(stream)
                self.frame_ready(image)
                stream.seek(0)
                self.wait_next_frame()
                if self.terminate:
                    break

    def pan_changed(self, pan_value):
        #The user has changed the pan in ui.
        #If you have a pan servo you can control it from here.
        #pan_value range is from -100 to 100 where zero is center.
        print("pan changed", pan_value)

    def tilt_changed(self, tilt_value):
        #The user has changed the tilt in ui.
        #If you have a tilt servo you can control it from here.
        #tilt_value range is from -100 to 100 where zero is center.
        print("tilt changed", tilt_value)

    def framerate_changed(self, fps_value):
        #The user has changed the frame rate in ui.
        #Update your camera settings to reflect the change.
        #fps_value range is 1, 5, 10, 20, 25, 30.
        print("fps changed", fps_value)


    def start_record(self):
        #The user has clicked on the start record button in ui.
        #Implement you save functionality here
        print("start record")

    def stop_record(self):
        #The user has stopped the recording in ui.
        print("stop record")

Cam_1()
