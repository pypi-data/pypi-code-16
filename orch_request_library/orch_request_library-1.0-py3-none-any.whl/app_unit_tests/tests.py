import django
import os
import uuid
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orch_request_library.settings")
django.setup()


from Request.TaskManager import *



#TaskManager.test_file_log("INFO","This is an unit test from unit_test_app")
print('testing start')
TaskManager.log_new_task("006b4960-8ae8-4292-9f24-7b09ae7346e4",uuid.uuid4(),"task2","server", "logs")