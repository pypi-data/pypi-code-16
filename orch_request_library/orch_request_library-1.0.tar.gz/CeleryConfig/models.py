from django.db import models

class RabbitMQ(models.Model):
    host_server = models.CharField(max_length=30)
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=30)

    @classmethod
    def get_rabbitmq_details(cls):
        return cls.objects.get(pk=1);



class CeleryConfigSettings(models.Model):
    app_name = models.CharField(max_length=120,default= "")
    celery_vhost = models.CharField(max_length=120, default="orch_default_vhost")
    celery_default_queue = models.CharField(max_length=120, default="orch_default_queue")
    celery_default_exchange = models.CharField(max_length=120, default="orch_default_queue_exchange")
    celery_default_exchange_type = models.CharField(max_length=120, default="direct")
    celery_default_routing_key = models.CharField(max_length=120, default="orch")
    celery_imports = models.CharField(max_length=120, default="")
    celery_result_backend= models.CharField(max_length=120, default="amqp")
    celery_result_exchange = models.CharField(max_length=120, default="orch_default_result_exchange")
    celery_result_exchange_type = models.CharField(max_length=120,  default="orch_default_result_exchange_type")
    updated_by =  models.CharField(max_length=256, default= "automation")
    updated_on = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_celery_settings(cls, app_name):
        return cls.objects.get(app_name=app_name)



