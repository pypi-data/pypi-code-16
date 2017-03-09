# -*- coding: utf-8 -*-
# =================================================================
#
# Authors: Pedro Dias <pedro.dias@ipma.pt>
#
# Copyright (c) 2016 Pedro Dias
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================
import os
from PIL import Image
from thumbnails.bbox import LonLatBoundingBox
from thumbnails.basemap import BasemapProviderFactory


class ThumbnailGenerator(object):
    """
    Class used to interface the catalogue with the thumbnail generation
    package.
    """
    @staticmethod
    def create_latlon_bbox(xmin, ymin, xmax, ymax):
        return LonLatBoundingBox(xmin, ymin, xmax, ymax)

    def __init__(self, config, bbox, width, height, provider='default'):
        if provider not in config:
            raise Exception

        self.provider_config = config[provider]
        self.bbox = bbox
        self.width = width
        self.height = height

    def fix_bbox(self):
        """
        Fix bounding box to the correct aspect ratio.
        """
        img_aspect_ratio = float(self.width) / float(self.height)

        bbox_width = self.bbox.xmax - self.bbox.xmin
        bbox_height = self.bbox.ymax - self.bbox.ymin
        center_x = self.bbox.xmin + bbox_width / 2.0
        center_y = self.bbox.ymin + bbox_height / 2.0
        bbox_aspect_ratio = float(bbox_width) / float(bbox_height)

        if img_aspect_ratio > bbox_aspect_ratio:
            width_ = img_aspect_ratio * bbox_height
            final_width = width_ * 1.1
            final_height = bbox_height * 1.1
            self.bbox = LonLatBoundingBox(
                center_x - (final_width / 2.0),
                center_y - (final_height / 2.0),
                center_x + (final_width / 2.0),
                center_y + (final_height / 2.0),
            )
        elif img_aspect_ratio < bbox_aspect_ratio:
            height_ = bbox_width / img_aspect_ratio
            final_height = height_ * 1.1
            final_width = bbox_width * 1.1
            self.bbox = LonLatBoundingBox(
                center_x - (final_width / 2.0),
                center_y - (final_height / 2.0),
                center_x + (final_width / 2.0),
                center_y + (final_height / 2.0),
            )


    def get_basemap(self, destination):
        """
        Creates the basemap image using the provided configuration
        to create a basemap provider.
        """
        provider_cls = BasemapProviderFactory.create_provider(self.provider_config['type'])
        provider = provider_cls(
            self.provider_config['layer'],
            self.provider_config['url'],
            self.bbox,
            self.provider_config['epsg'],
            self.width,
            self.height
        )

        return provider.retrieve(destination)

    def get_service(self, destination, url, layer, **kwargs):
        """
        Creates the service image to be used to create the thumbnail
        """
        provider_cls = BasemapProviderFactory.create_provider('wms')
        provider = provider_cls(
            layer,
            url,
            self.bbox,
            self.provider_config['epsg'],
            self.width,
            self.height,
            username=kwargs.pop('username', None),
            password=kwargs.pop('password', None),
        )

        return provider.retrieve(destination, transparent=True)

    def _convert_alpha(self, filepath):
        base = Image.open(filepath)
        base_alpha = Image.new('RGBA', (self.width, self.height))
        base_alpha.paste(base)
        base.close()
        return base_alpha

    def generate_thumbnail(self, target, url, layer, tmp, **kwargs):
        """
        Generates the thumbnail image.
        """
        basemap_destination = os.path.join(tmp, 'basemap.png')
        service_destination = os.path.join(tmp, 'service.png')

        self.fix_bbox()
        self.get_basemap(basemap_destination)
        self.get_service(service_destination, url, layer, **kwargs)

        basemap_alpha = self._convert_alpha(basemap_destination)
        service_alpha = self._convert_alpha(service_destination)

        final = Image.alpha_composite(basemap_alpha, service_alpha)
        final.save(target)
        final.close()
        return target
