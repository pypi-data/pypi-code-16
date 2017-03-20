from django.db import models
import uuid

class ApiRequest(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    requestId = models.CharField(max_length=256)
    apiToken = models.CharField(max_length=64, verbose_name=u"API Token", default="")

    requestPath = models.TextField()
    requestQueryString = models.TextField()
    requestVars = models.TextField()
    requestMethod = models.CharField(max_length=4)
    requestSecure = models.BooleanField(default=False)
    requestAjax = models.BooleanField(default=False)
    requestMETA = models.TextField(null=True, blank=True)
    requestAddress = models.GenericIPAddressField()
    requestBody = models.TextField(null=True, blank=True)

    viewFunction = models.CharField(max_length=256)
    viewDocString = models.TextField(null=True, blank=True)
    viewArgs = models.TextField()

    responseCode = models.CharField(max_length=3)
    responseContent = models.TextField()

    def __str__(self):
        return self.requestId

    @classmethod
    def getApiRequests(cls):
        return cls.objects.get(pk=3)


class TaskDetails(models.Model):
    TASK_SEVERITY = (
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'HIGH'),
    )

    TASK_STATUS = (
        ('0', 'Active'),
        ('1', 'Completed'),
        ('2', 'Defferred'),
        ('3', 'Cancelled'),
    )


    request_id = models.ForeignKey(ApiRequest, on_delete=models.CASCADE)
    task_id = models.UUIDField()
    task_name = models.CharField(max_length=200)
    task_source = models.CharField(max_length=200)
    task_destination = models.CharField(max_length=200)
    task_severity = models.CharField(max_length=1, choices=TASK_SEVERITY)
    task_status = models.CharField(max_length=1, choices=TASK_STATUS)
    initiated_on = models.DateTimeField(auto_now_add=True)
    completed_on = models.DateTimeField(auto_now_add=True)
    parent_task_id =models.UUIDField()

    def __str__(self):
        return self.task_id


class TaskLog(models.Model):
    LOG_TYPE = (
        ('0', 'DEBUG'),
        ('1', 'WARNING'),
        ('2', 'INFO'),
        ('3', 'ERROR'),
        ('4', 'CRITICAL'),
    )

    task_id = models.ForeignKey(TaskDetails, on_delete=models.CASCADE)
    task_log_type = models.CharField(max_length=1, choices=LOG_TYPE)
    task_message = models.TextField()
    logged_on = models.DateTimeField(auto_now_add=True)