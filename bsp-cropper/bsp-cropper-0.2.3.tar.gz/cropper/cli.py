#!/usr/bin/env python

import os
from glob import glob

import click
from PIL import Image

from devices import DEVICES


def create_intermediate_dirs(path):
    dir_path = os.path.dirname(path)
    try:
        os.makedirs(dir_path)
    except OSError:
        pass


def transform_images(src_paths, dest_paths, resize_to, crop_margins):
    for (src, dest) in zip(src_paths, dest_paths):
        src_image = Image.open(src)
        final_image = src_image

        # resize
        if resize_to:
            final_image = src_image.resize(resize_to, Image.LANCZOS)

        # crop
        if crop_margins:
            # left, upper, right, lower
            cropped_size = (0 + crop_margins[0]/2, 0, resize_to[0] - crop_margins[0]/2, resize_to[1]-crop_margins[1])
            final_image = final_image.crop(cropped_size)

        # save
        create_intermediate_dirs(dest)
        final_image.save(dest)


@click.command()
@click.argument('master_dir', type=str)
def main(master_dir):
    master_dir = os.path.abspath(master_dir)

    iphone_images_pattern = os.path.join(master_dir, 'iPhoneMaster') + '/*/*.png'
    ipad_images_pattern = os.path.join(master_dir, 'iPadMaster') + '/*/*.png'
    # ipad_images_pattern = os.path.join(dir, 'iOS-iPad-Pro')

    iphone_img_paths = glob(iphone_images_pattern)
    ipad_img_paths = glob(ipad_images_pattern)

    if not iphone_img_paths:
        print "Error: no master iPhone images found!"
        exit(1)

    if not ipad_img_paths:
        print "Error: no master iPad images found!"
        exit(1)

    # iphone screenshots
    for device_name, operations in DEVICES['iPhone'].items():
        dest_paths = [img_path.replace('iPhoneMaster', device_name) for img_path in iphone_img_paths]
        transform_images(iphone_img_paths, dest_paths, operations['resize'], operations['crop'])

    # ipad screenshots
    for device_name, operations in DEVICES['iPad'].items():
        dest_paths = [img_path.replace('iPadMaster', device_name) for img_path in ipad_img_paths]
        transform_images(ipad_img_paths, dest_paths, operations['resize'], operations['crop'])

main()
