# -*- coding: utf-8 -*-
from os.path import join, expanduser


# Settings
PATH_BIN_LEMMES = join(expanduser("~"), 'lemmes')
LANG = 'es'
SOURCE_LEMMAS_CSV = 'lemmas.csv'
FILE_LEMMAS_CSV = join(PATH_BIN_LEMMES, 'lemmes.csv')
FILE_LEMMAS_BIN = join(PATH_BIN_LEMMES, 'lemmes.pk')
LOG_FILE = '/var/log/lemmes.log'
RESOURCES_URL = 'https://s3-us-west-2.amazonaws.com/lemmes'
