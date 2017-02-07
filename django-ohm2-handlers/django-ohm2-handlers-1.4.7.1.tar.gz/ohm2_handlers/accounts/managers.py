from django.db import models
from ohm2_handlers import utils as h_utils
from ohm2_handlers.accounts import settings
from unidecode import unidecode
import os

def avatars_upload_to(instance, filename):
	
	file_name = h_utils.to_unicode(filename.strip(), True, "_")
	file_name = h_utils.random_string(32) + "." + file_name.rsplit(".", 1)[-1]
	return os.path.join(settings.AVATARS_UPLOAD_TO, instance.user.avatars.identity, file_name)