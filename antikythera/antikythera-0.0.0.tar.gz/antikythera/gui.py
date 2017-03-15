#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" gui.py

The GUI for antikythera

"""
import sys
import logging
import multiprocessing as mp

# Fix kivy's logging
import antikythera.kivylogs
from kivy.logger import Logger

from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.clock import Clock, mainthread
from kivy.uix.gridlayout import GridLayout
from multiprocessing import Queue
from time import sleep


from antikythera import __version__
from antikythera.antikythera import Anti, create_parser

_logger = logging.getLogger(__name__)

__author__= "Finding Ray"
__copyright__ = "Finding Ray"
__license__ = "GNU GPLv3+"


# Todo: move this to config file
Builder.load_string("""
<AnimWidget@Widget>:
    canvas:
        Color:
            rgba: 13/255, 134/255, 178/255, 1
        Rectangle:
            pos: self.pos
            size: self.size
    size_hint: None, None
    size: 400, 30


<RootWidget>:
    cols: 1

    canvas:
        Color:
            rgba: 24/255, 27/255, 30/255, 1
        Rectangle:
            pos: self.pos
            size: self.size

    anim_box: anim_box
    detect_button: detect_button
    status: status
    defcon: defcon

    Button:
        id: detect_button
        font_size: 30
        background_color: 255/255, 32/255, 82/255, 1
        background_normal: ''
        text: 'Find a Stingray!'
        on_press: app.start()

    Label:
        id: status
        font_size: 30
        color: 13/255, 134/255, 178/255, 1
        text_size: self.width, None
        halign: 'center'

    AnchorLayout:
        id: anim_box

    Label:
        id: defcon
        font_size: 100
        color: 178/255, 5/255, 44/255, 1
        text: '5'
""")


class RootWidget(GridLayout):
    """

    """
    def start_detector(self):
        """

        """
        _logger.info("GUI: Starting detector")
        self.detecting()


    def detecting(self, *args):
        """

        """
        # Remove start button and add status
        self.remove_widget(self.detect_button)
        self.status.text = ('Looking for a stingray...')

        # Spinny Widget
        action_bar = Factory.AnimWidget()
        self.anim_box.add_widget(action_bar)
        animation = Animation(opacity=0.3, width=10, duration=0.6)
        animation += Animation(opacity=1, width=400, duration=0.8)
        animation.repeat = True
        animation.start(action_bar)


    def update_defcon(self, new_text):
        self.defcon.text = new_text


    def update_status(self, new_text):
        self.status.text = new_text



class MetricDisplay(App):
    """

    """

    def __init__(self, *args, **kwargs):
        super(MetricDisplay, self).__init__(*args, **kwargs)
        self.IMSI_detector = None

    def on_start(self):
        """

        """
        parser = create_parser()
        args = parser.parse_args(sys.argv[1:])

        if args.loglevel:
            Logger.setLevel(level=args.loglevel)
        else:
            #loglevel = LOG_LEVELS.get(Config.get(['kivy', 'log_level']))
            Logger.setLevel(level=logging.WARNING)

        self.IMSI_detector = Anti(args.threads, args.headless, interface=args.interface, capturefile=args.pcap, max_qsize=args.qsize)



    def build(self):
        """

        """
        return RootWidget()

    def start(self):
        self.IMSI_detector.start()
        self.root.start_detector()


    def on_stop(self):
        """

        """
        if self.IMSI_detector.is_alive():
            _logger.info("GUI: Sending shutdown signal to Anti")
            self.IMSI_detector.shutdown()
            _logger.info("GUI: Joining Anti process {}".format(self.IMSI_detector.pid))
            self.IMSI_detector.join()
        _logger.info("GUI: Shutdown successfully".format(self.IMSI_detector.pid))


def run():
    """

    """
    _logger.info("GUI: Starting GUI App")
    MetricDisplay().run()


if __name__ == "__main__":
    run()
