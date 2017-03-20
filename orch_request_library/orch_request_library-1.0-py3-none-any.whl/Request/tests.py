import django
from FileLogs.FileLogManager import *
from .TaskManager import *
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orch_request_library.settings")
django.setup()


#FileLogManager.write_log_to_file("INFO","This is the request--new test")
TaskManager.log_new_task("15e593a2-f75d-45a9-8142-8ecbf90b2e14","3a51cbca-48ba-400a-97d7-bbab17d2948e","task1","test", "logs")