# Enable remote debugging for VSCode
from .base import *  # noqa

import ptvsd
ptvsd.enable_attach("theworstkeptsecret", address=("0.0.0.0", 8010))

url = os.getenv("CONTENTWORKSHOP_URL") or "https://contentworkshop.learningequality.org"

DEBUG = True