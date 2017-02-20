from gopro.camera import Camera


__camera = Camera()

def start():
    __camera.start()

def stop():
    __camera.stop()
