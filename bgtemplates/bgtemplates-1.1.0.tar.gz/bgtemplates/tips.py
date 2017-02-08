"""
Module that initializes a list that appends each new :class:`Tip`.
It is used to show all the tips in the list when the :func:`show_tips` is called
"""

import logging
from colorama import init, Style, Fore


tips = []


class Tip:

    def __init__(self, message, cmd=None):
        """
        Creates a tip message to be displayed and add it to the tips list

        Args:
            message (str): message
            cmd (str): optional command to be displayed as complementary information for the message

        """
        msg = Fore.GREEN + Style.BRIGHT + 'TIP >>> '
        msg += Style.RESET_ALL + message
        if cmd is not None:
            msg += ':\t' + Fore.GREEN + '$ ' + cmd
        msg += Style.RESET_ALL
        tips.append(msg)


def show_tips():
    """
    Display all tips
    """
    init()  # initialized the colorama package
    for tip in tips:
        logging.info(tip)
