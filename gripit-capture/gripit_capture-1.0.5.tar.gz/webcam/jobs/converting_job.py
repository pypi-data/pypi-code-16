import getpass

from webcam.config import Config
from webcam.services.cmd import Cmd


class ConvertingJob:
    def __init__(self):
        self.job_running = False
        self.cmd = Cmd()

    def convert(self, file):
        print("START CONVERSION")
        self.job_running = True
        self.cmd.run(self.__convert_command(file))

    def stop(self):
        print("STOP CONVERSION")
        self.cmd.kill()
        self.job_running = False

    def is_running(self):
        return self.job_running

    def __convert_command(self, file):
        user_name = getpass.getuser()
        return '/home/' + user_name + '/bin/ffmpeg -i ' + \
               file + Config.OUTPUT_FILE_EXTENSION + \
               ' -vcodec libx264 ' + \
               file + '_h264' + Config.OUTPUT_FILE_EXTENSION + ' &'
