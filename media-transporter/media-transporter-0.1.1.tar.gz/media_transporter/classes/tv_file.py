import os
from media_transporter import config
from . import Logger, MediaFile


class TvFile(MediaFile):
    """Class to handle specific actions when dealing with a TV show file.

    TvFile performs tv-specific tasks, including specific logging
    messages and checking for already-existing shows/episodes on the media share.

    Attributes
    ----------
        download_path: str
            Full path to the file being operated on.
        file_name: str
            Name of the file being operated on.
        show_info: tuple
            Tuple consisting of matched regular expression groups identifying
            the specific file as a TV show.

    """

    def __init__(self, download_path, file_name, show_info):
        title, episode_id, season, episode = show_info
        self.episode_id = episode_id
        self.season = int(season)
        self.episode = int(episode)
        MediaFile.__init__(self, download_path, file_name, title)

    def prepare_destination(self):
        """Checks if there is storage capacity on the media share,
        and if there is, attempt to make the TV show's directory structure
        on the media share in advance of extracting and moving."""
        self.tv_root_path = config.share_tv_root_path % (
            self.share_path, self.title)
        self.tv_season_path = config.share_tv_season_path % (
            self.share_path, self.title, self.season)

        if os.path.isdir(self.tv_root_path):
            if self.capacity_reached():
                Logger.log('[!] Capacity reached. Skipping adding Season %s of %s.' % (
                    self.season, self.title))
            else:
                if not os.path.isdir(self.tv_season_path):
                    Logger.log('[+] Creating folder for Season %s of %s' %
                               (self.season, self.title))
                    os.mkdir(self.tv_season_path)
        else:
            if self.capacity_reached():
                Logger.log(
                    '[!] Capacity reached. Skipping adding show %s.' % self.title)
            else:
                Logger.log('[+] Adding TV Show: %s' % self.title)
                os.makedirs(self.tv_season_path)

    def process(self):
        """Checks if a TV show already has a directory created on the media share.
        Directly moves a media file to its destination, or extracts and moves the
        movie from a RAR archive."""
        existing_episodes = os.listdir(self.tv_season_path)
        if not [episode for episode in existing_episodes if self.episode_id in episode]:
            if self.has_video_extension:
                self.move_media()
            else:
                self.extract_media()
