
from celery import Celery

app = Celery('tasks', broker='pyamqp://root:null@localhost/myvhost')

app.config_from_object('django.conf:settings')
@app.task
def add(x, y):
    return x + y

@app.task()
def multiply(x,y):
    return x * y
