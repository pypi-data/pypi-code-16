from __future__ import absolute_import
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from ohm2_handlers import utils as h_utils
from . import models as countries_models
import time, random, datetime


@shared_task()
def countries_test_task():
	pass