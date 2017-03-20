#from celery import Celery
#from CeleryConfig.CeleryManager import *
from .models import TaskDetail, TaskLog, ApiRequest
from FileLogs.FileLogManager import *

class TaskManager:
    @classmethod
    def log_new_task(cls, request_id, task_id, task_name, source, destination):
        try:
            request = ApiRequest.objects.get(requestId= request_id)

            task_details = TaskDetail(
                request_id=request,
                task_id=task_id,
                task_name=task_name,
                task_source=source,
                task_destination=destination,
                task_severity='0'
            )
            task_details.save()

            message = 'Task ID:[' + str(task_id) + '] assigned to Request ID [' + str(request_id) + ']'
            TaskManager.add_task_log(task_id, 2, message)

        except Exception as ex:
            print(str(ex))

    @classmethod
    def add_task_log(cls, task_id, log_type, message):
        try:
            task_details = TaskDetail.objects.get(task_id=task_id)

            task_log = TaskLog(
                task_id=task_details,
                task_log_type=log_type,
                task_message=message
            )

            task_log.save()
        except Exception as ex:
            print(str(ex))


    @classmethod
    def test_file_log(cls, log_level, log_message):

        source = stack()[1]
        module_details = getmodule(source[0])
        module_match = re.search("<module '(.+?)' from", str(module_details))

        if module_match:
            module_name = module_match.group(1)

        print(module_name)
        FileLogManager.write_log_to_file(log_level, log_message, "")

    # @classmethod
    # def log_new_task_via_celery(cls, request_id, task_id, task_name, source, destination):
    #     try:
    #         celery_app = CeleryManager.create_celery_app("orch_service_logger")
    #         task_details = TaskDetails(
    #             request_id= request_id,
    #             task_id = task_id,
    #             task_name= task_name,
    #             task_source = source,
    #             task_destination= destination,
    #             task_severity= '0'
    #         )
    #
    #         celery_app.send_task('log_task_details', task_details=task_details)
    #     except:
    #         pass
    #
    # @classmethod
    # def add_task_log_via_celery(cls, task_id, log_type, message):
    #     try:
    #         celery_app = CeleryManager.create_celery_app("orch_service_logger")
    #         task_details = TaskLog(
    #             task_id = task_id,
    #             task_name= log_type,
    #             task_message=message
    #         )
    #
    #         celery_app.send_task('add_task_log', task_details=task_details)
    #     except:
    #             pass
