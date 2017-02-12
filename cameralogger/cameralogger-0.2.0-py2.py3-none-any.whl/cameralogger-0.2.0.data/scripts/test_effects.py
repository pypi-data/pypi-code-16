#!python

# Cameralogger - record and decorate camera images for timelapses etc.
# Copyright (C) 2017  Steve Marple.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import cameralogger
import argparse
import datetime
from fractions import Fraction
import logging
import numpy as np
import os
from PIL import Image
import six
import subprocess
import time
from cameralogger.ffmpeg import FFmpeg
from cameralogger import MovieTasks

logger = logging.getLogger(__name__)
logging.basicConfig(level='DEBUG')

config = cameralogger.read_config_file(os.path.join(os.path.expanduser('~'), 'test_effects.ini'))

output_filename = os.path.join(os.path.expanduser('~'), 'test_effects.mp4')
size = [960, 720]
ifr = 60
ofr = Fraction(60, 1)
ffmpeg = FFmpeg(output_filename, size, ifr, ofr)

tasks = MovieTasks(ffmpeg, config, 'timelapse')
pink = Image.new('RGB', size, 'pink')
orange = Image.new('RGB', size, 'orange')
white = Image.new('RGB', size, 'white')

ffmpeg.fade_in(pink, 180)
ffmpeg.freeze(pink, 60)
ffmpeg.freeze(orange, 60)
ffmpeg.freeze(white, 60)
ffmpeg.dissolve(pink, orange, 180)
ffmpeg.set_background('white')
ffmpeg.fade_out(orange, 240)
task_list = cameralogger.get_config_option(config, 'movie', 'tasks', default='')

tasks.run_tasks(task_list.split())