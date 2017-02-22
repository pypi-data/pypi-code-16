import os
import shutil
import re
import glob
import subprocess
from . import Storage, Logger, TransportException
from media_transporter import config

flatten_list = lambda l: [item for sublist in l for item in sublist]
"""lambda: lambda function to flatten a list of nested lists to a single list."""


class MediaFile(Storage):
    """Generic class to perform tasks required by both TvFile and MovieFile.

    MediaFile mainly handles common functions such as extracting and moving
    media files from one place to another. This class is also responsible
    for light text formatting of media titles.

    MediaFile inherits from the Storage class, allowing MediaFile to access
    methods and parameters essential to the process of moving files from one
    place to another.

    Attributes
    ----------
        download_path: str
            Full path to the file being operated on.
        file_name: str
            Name of file being operated on.
        title: string
            Original name of the media file. `title` is
            transformed to a human-readable format inline.
        has_video_extension: bool
            Returns True when `file_name` has an acceptable
            media file extension.

    """

    def __init__(self, download_path, file_name, title):
        self.file_name = file_name
        self.title = re.sub(r'(\.|_){1,}', ' ', title)
        self.download_path = download_path
        self.has_video_extension = self.file_name.endswith(
            ('mkv', 'avi', 'mp4', 'mov'))

        if os.path.isdir('%s/%s' % (download_path, file_name)):
            os.chdir('%s/%s' % (download_path, file_name))
        Storage.__init__(self)

    def move_media(self):
        """Moves a file from a download path to its final destination
        on the media share."""
        from . import TvFile, MovieFile

        if isinstance(self, MovieFile):
            Logger.log('[-] Movie %s wasn\'t found. Moving...' % self.title)
        elif isinstance(self, TvFile):
            Logger.log('[-] %s Season %s Episode %s wasn\'t found. Moving...' %
                       self.title, self.season, self.episode)
        shutil.move('%s/%s' % (self.download_path, self.file_name),
                    self.movie_root_path)

    def extract_media(self):
        """Extracts a media file from a series of RAR files, then moves it
        to its final destination on the media share."""
        from . import TvFile, MovieFile

        rar_files = glob.glob('*.rar')
        unrar_command = '%s x %s &>/dev/null' % (
            config.unrar_path, rar_files[0])
        try:
            destination_path = ''
            message = '[-] %s wasn\'t found. Extracting and moving...'
            if isinstance(self, TvFile):
                destination_path = self.tv_season_path
                Logger.log(message % '%s Season %s Episode %s' %
                           (self.title, self.season, self.episode))
            elif isinstance(self, MovieFile):
                destination_path = self.movie_root_path
                Logger.log(message % self.title)

            subprocess.check_output(unrar_command, shell=True)
            extracted_files = flatten_list([glob.glob(extension) for extension in [
                                           '*.mkv', '*.avi', '*.mp4', '*.mov']])
            for file in extracted_files:
                shutil.move(file, destination_path)
        except Exception as e:
            raise TransportException('[!] runtime error: %s.' % e, True)
