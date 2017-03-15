#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
# @date: Wed 15 Feb 2017 15:35:36 CET

"""
Given an periocular image, computes the grid graph and show in the image

Usage:
  show_periocular_jets.py <input_image> <output_image>
  show_periocular_jets.py -h | --help
Options:
  -h --help           Show this screen.
"""

import bob.io.base
import bob.io.image
import bob.ip.draw
import bob.ip.color
from bob.bio.pericrosseye_competition.extractor import EyeGraph


def main():
    from docopt import docopt

    args = docopt(__doc__, version='Show the the position of the jets')

    input_image = bob.io.base.load(args["<input_image>"])
    output_image = args["<output_image>"]
    
    distances = [50, 100, 150, 200, 250]
    n_angles = 20
    eye_graph = EyeGraph(distances = distances,
                         n_points  = n_angles,
                         landmark_offset=20)

    process_image = input_image.copy()
    if process_image.ndim == 3:
        process_image = bob.ip.color.rgb_to_gray(input_image)

    left, center_up, right, center_down = eye_graph.get_landmarks(process_image.astype("uint8"))
    
    # Plotting the base coords
    if len(input_image.shape) == 2:
        input_image = bob.ip.color.gray_to_rgb(input_image)
    
    colors = [(255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255)]
    bob.ip.draw.plus(input_image, left, radius=10, color=colors[0])
    bob.ip.draw.plus(input_image, right, radius=10, color=colors[1])
    bob.ip.draw.plus(input_image, center_up, radius=10, color=colors[2])
    bob.ip.draw.plus(input_image, center_down, radius=10, color=colors[3])

    i = 0
    for c in eye_graph.get_jets_coords([left, center_up, right, center_down], process_image):

        # One color per side
        index = i / (n_angles+1)
        if index==4:
            index=0; i = 0

        bob.ip.draw.plus(input_image, c, radius=10, color=colors[index])
        i += 1
    
    bob.io.base.save(input_image.astype("uint8"), output_image)

