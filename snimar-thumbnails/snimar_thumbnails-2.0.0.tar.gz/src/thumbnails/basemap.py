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
from owslib.wmts import WebMapTileService
from owslib.wms import WebMapService


class WebServiceBasemapProvider(object):
    """
    Base class used to setup a basemap provider that implements
    an OGC service.
    """
    def __init__(self, url, bbox, epsg, width, height):
        self.provider_url = url
        self.bbox = bbox
        self.width = width
        self.height = height
        self.epsg = int(epsg)

    def epsg_code(self):
        return 'EPSG:{}'.format(int(self.epsg))

    def retrieve(self):
        raise NotImplementedError


class WMSBasemapProvider(WebServiceBasemapProvider):
    """
    Class used to setup and retrieve a basemap that is provided
    via Web Map Service.
    """
    SERVICE_NAME = 'wms'

    def __init__(self, layer, url, bbox, epsg, width, height, **kwargs):
        super(WMSBasemapProvider, self).__init__(url, bbox, epsg, width, height)
        self.service = WebMapService(
            self.provider_url,
            username=kwargs.pop('username', None),
            password=kwargs.pop('password', None),
        )
        self.layer = layer
        self._validate()

    def _validate(self):
        """
        Perform simple validations after instance initialization. If the
        validation fails, an exception is raised to cancel instance creation.
        """
        if self.layer not in self.service.contents.keys():
            raise Exception
        content = self.service.contents[self.layer]
        if self.epsg_code() not in content.crsOptions:
            raise Exception

    def retrieve(self, destination, **kwargs):
        payload = {
            'layers': [self.layer],
            'srs': self.epsg_code(),
            'bbox': [self.bbox.xmin, self.bbox.ymin, self.bbox.xmax, self.bbox.ymax],
            'size': [self.width, self.height],
            'format': 'image/png',
            'transparent': kwargs.pop('transparent', False),
        }

        image = self.service.getmap(**payload)
        with open(destination, 'wb') as fp:
            fp.write(image.read())

        return [destination]


class WMTSBasemapProvider(WebServiceBasemapProvider):
    """
    Class used to setup and retrieve a basemap that is provided
    via Web Map Tile Service.
    """
    SERVICE_NAME = 'wmts'

    def __init__(self, url, layer, bbox, epsg, width, height):
        super(WMTSBasemapProvider, self).__init__(url, bbox, epsg, width, height)
        self.service = WebMapTileService(self.provider_url)

    def provider_layers(self):
        return self.service.contents.keys()

    def retrieve(self):
        return None


class BasemapProviderFactory(object):
    """
    Class factory used to dynamically create a basemap provider
    instance based in the configuration data.
    """
    BASE_PROVIDER = WebServiceBasemapProvider

    @classmethod
    def create_provider(cls, config):
        for subcls in cls.BASE_PROVIDER.__subclasses__():
            if not hasattr(subcls, 'SERVICE_NAME'):
                continue

            if config.lower() == getattr(subcls, 'SERVICE_NAME').lower():
                return subcls
