import glob
import re
import os
import datetime
import logging


class RunRotatingHandler(logging.FileHandler):
    ROTATING_FILE_PATH = None

    def __init__(self, dir_path, backup_count=None):
        filepath = self.setRotatingFilePath(dir_path, backup_count)
        super().__init__(filepath)

    def setRotatingFilePath(self, dir_path, backup_count):
        if not RunRotatingHandler.ROTATING_FILE_PATH is None:
            return RunRotatingHandler.ROTATING_FILE_PATH

        # log pattern
        pattern = r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}.log$'
        files = sorted(glob.glob(os.path.join(dir_path, '*')))
        # get file only match pattern
        matche_files = []
        for file in files:
            match = re.findall(pattern, file)
            if len(match) != 0:
                matche_files.append(file)

        if len(matche_files) >= backup_count:
            os.remove(matche_files[0])
        filename = datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
        filepath = os.path.join(dir_path, filename + '.log')
        print('run rotating log file is output in [{}]'.format(
            os.path.abspath(filepath)))

        RunRotatingHandler.ROTATING_FILE_PATH = filepath
        return RunRotatingHandler.ROTATING_FILE_PATH
