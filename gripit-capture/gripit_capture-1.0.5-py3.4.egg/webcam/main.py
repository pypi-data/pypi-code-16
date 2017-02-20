from webcam.camera import Camera

__camera = Camera()


def access():
    __camera.access()


def start_recording():
    __camera.start_recording()


def create_file(name):
    __camera.create_file(name)


def stop_recording():
    __camera.stop_recording()


def release():
    __camera.release()
