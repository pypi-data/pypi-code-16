import datetime
from kervi.camera import FrameCamera
from PIL import Image, ImageDraw

class Cam_1(FrameCamera):
    def __init__(self):
        FrameCamera.__init__(self, "cam1", "camera 1")
        self.font = self.get_font()

    def capture_frames(self):
        while not self.terminate:
            image = Image.new('RGBA', size=(self.width, self.height), color=(155, 0, 0))
            draw = ImageDraw.Draw(image)
            draw.rectangle([(self.width/2-50, self.height/2-50), (self.width/2+50, self.height/2+50)])
            draw.rectangle([(10, 10), (self.width-10, self.height-10)])
            picture_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
            draw.text((15, 15), picture_time[:-5], font=self.font)
            self.frame_ready(image)
            self.wait_next_frame()

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
