import os
from . import MediaFile, Logger
from media_transporter import config


class MovieFile(MediaFile):
    """Class to handle specific actions when dealing with a Movie file.

    MovieFile performs movie-specific tasks, including specific logging
    messages and checking for already-existing Movies on the media share.

    Attributes
    ----------
        download_path: str
            Full path to the file being operated on.
        file_name: str
            Name of the file being operated on.
        movie_info: tuple
            Tuple consisting of matched regular expression groups identifying
            the specific file as a Movie.

    """

    def __init__(self, download_path, file_name, movie_info):
        title, year, resolution = movie_info
        MediaFile.__init__(self, download_path, file_name, title)

    def prepare_destination(self):
        """Checks if there is storage capacity on the media share,
        and if there is, attempt to make the Movie's directory structure
        on the media share in advance of extracting and moving."""
        self.movie_root_path = config.share_movie_root_path % (
            self.share_path, self.title)

        if os.path.isdir(self.movie_root_path):
            if self.capacity_reached():
                Logger.log(
                    '[!] Capacity reached. Skipping adding movie %s.' % self.title)
            else:
                if not os.path.isdir(self.movie_root_path):
                    Logger.log('[+] Adding Movie: %s' % self.title)
                    os.mkdir(self.movie_root_path)

    def process(self):
        """Checks if a Movie already has a directory created on the media share.
        Directly moves a media file to its destination, or extracts and moves the
        movie from a RAR archive."""
        existing_movie = os.listdir(self.movie_root_path)
        if not [movie for movie in existing_movie if self.title in movie]:
            if self.has_video_extension:
                self.move_media()
            else:
                self.extract_media()
