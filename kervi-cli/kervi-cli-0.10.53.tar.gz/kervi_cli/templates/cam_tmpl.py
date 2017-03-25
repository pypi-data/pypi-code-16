import datetime
from kervi.camera import CameraStreamer
from PIL import Image, ImageDraw

class Cam_1(CameraStreamer):
     def __init__(self):
         CameraStreamer.__init__(self, "cam1", "camera 1")
         self.font = self.get_font()

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


Cam_1()
