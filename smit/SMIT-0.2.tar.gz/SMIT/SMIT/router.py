

class MyRouter(object):
  def route_for_task(self, task, args=None, kwargs=None):
    return {'exchange': 'celery',
      'exchange_type': 'direct',
      'queue': task,
      'routing_key': task
    }
