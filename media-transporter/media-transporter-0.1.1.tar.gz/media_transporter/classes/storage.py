import os
import subprocess
from . import TransportException
from media_transporter import config


class Storage():
    """Class to manage storage-specific functions related to
    dealing with a configured media share.

    Attributes
    ----------
        share_path: str
            First available media share path with available capacity.

    """

    def __init__(self):
        self.share_path = self.locate_media_share()

    def locate_media_share(self):
        """Reads the `media_shares` config string and chooses
        the first available media share path.

        Returns
        -------
            string
                Path to media share.
            TransportException
                Raised exception when media share was not found.
        """
        media_shares = config.media_shares
        for path in media_shares.split(','):
            if os.path.isdir(path):
                return path
            raise TransportException(
                '[!] Media Share %s was not found, terminating...' % path, True)

    def get_volume_capacity(self):
        """Determines the storage capacity of the targeted media share.

        TODO: customize for use with other, non-UNIX systems

        Returns
        -------
            list
                System output of available disk space is on the selected
                media share
        """
        command = """df -H %s | tail -n1 | awk '{ print $5 " " $4 }'""" % self.share_path
        command_output = subprocess.check_output(command, shell=True)
        return command_output.split(' ')

    def capacity_reached(self):
        """Interprets the result of `get_volume_capacity()` and checks
        if it is above or below the `safe_capacity_percentage` config value.

        Returns
        -------
            bool
                True when below the capacity, False when at or above the capacity.
        """

        percentage_free, available_space = self.get_volume_capacity()
        percentage_free = int(percentage_free.replace('%', ''))
        if percentage_free >= int(config.safe_capacity_percentage):
            return True
        return False
