#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""Main Celery Application"""

from celery import Celery

app = Celery('doit',
             broker='redis://127.0.0.1:6479/0',
             # add result backend here if needed.
             backend='redis://127.0.9.1:6479/0')

# The flllowing is the celery routes
# app.conf.CELERY_ROUTES = {}

app.conf.CELERY_ACCEPT_CONTENT = ['json']
app.conf.CELERY_TASK_SERIALIZER = 'json'
app.conf.CELERY_RESULT_SERIALIZER = 'json'

if __name__ == '__main__':
    app.start()
