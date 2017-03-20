from celery import Celery
from .models import *

class CeleryManager:
    @classmethod
    def get_celery_object(cls, app_name):
        return  CeleryConfigSettings.get_celery_settings(app_name)

    @classmethod
    def create_celery_app(cls, app_name):
        try:
            app = None
            rabbit_mq = RabbitMQ.get_rabbitmq_details()
            if (rabbit_mq is None):
                pass

            obj = CeleryManager.get_celery_object(app_name)

            if (obj is None):
                pass

            broker = "amqp://" + rabbit_mq.username + ":" + rabbit_mq.password + "@" + rabbit_mq.host_server + "/" + obj.celery_vhost
            app = Celery(broker=broker)
            app.conf.update(
                CELERY_DEFAULT_QUEUE=obj.celery_default_queue,
                CELERY_DEFAULT_EXCHANGE=obj.celery_default_exchange,
                CELERY_DEFAULT_EXCHANGE_TYPE=obj.celery_default_exchange_type,
                CELERY_DEFAULT_ROUTING_KEY=obj.celery_default_routing_key,
                CELERY_IMPORTS=(obj.celery_imports),
            )
        except RabbitMQ.DoesNotExist:
            print('Celery settings not found for app [' + app_name + ']')
            pass
        except CeleryConfigSettings.DoesNotExist:
            print('Celery settings not found for app [' + app_name + ']')
            pass

        return app