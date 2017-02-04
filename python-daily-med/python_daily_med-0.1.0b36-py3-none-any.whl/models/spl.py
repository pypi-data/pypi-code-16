# -*- coding: utf-8 -*-
# Copyright 2017-TODAY LasLabs Inc.
# License MIT (https://opensource.org/licenses/MIT).

import xmltodict

from .base_model import BaseModel


class SPLMeta(BaseModel):
    """ SPLMeta provides the metadata for a Structured Product Label """

    def __init__(self, **kwargs):
        """ It initializes the SPL object.

        Args:
            set_id (str):
            title (str):
            spl_version (str):
            published_date (str):
        """
        kwargs['published_date'] = self.str_to_date(kwargs['published_date'])
        super(SPLMeta, self).__init__(**kwargs)


class SPLDocument(BaseModel):
    """ SPLDocument provides the data for a Structured Product Label """

    def __init__(self, xml):
        """ It initializes the SPLDocument object.

        Args:
            xml (str): The XML SPL Document data, as provided by DailyMed.
        """
        spl_doc = xmltodict.parse(xml)['document']
        super(SPLDocument, self).__init__(**spl_doc)
