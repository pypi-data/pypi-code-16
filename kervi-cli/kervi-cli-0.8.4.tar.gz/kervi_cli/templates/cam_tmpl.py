import datetime
from kervi.camera import FrameCamera
from PIL import Image, ImageDraw

class Cam_1(FrameCamera):
    def __init__(self):
        FrameCamera.__init__(self, "cam1", "camera 1")
        self.font = self.get_font()

    def get_frame(self, height, width):
        image = Image.new('RGBA', size=(width, height), color=(155, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rectangle([(width/2-50, height/2-50), (width/2+50, height/2+50)])
        draw.rectangle([(10, 10), (width-10, height-10)])
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
        draw.text((15, 15), time[:-5], font=self.font)
        return image

    def pan_changed(self, pan_value):
        #The user has changed the pan in ui.
        #If you have a pan servo you can control it from here.
        #pan_value range is from -100 to 100 where zero is center.
        print ("pan changed", pan_value)

    def tilt_changed(self, tilt_value):
        #The user has changed the tilt in ui.
        #If you have a tilt servo you can control it from here.
        #tilt_value range is from -100 to 100 where zero is center.
        print ("tilt changed", tilt_value)

Cam_1()
