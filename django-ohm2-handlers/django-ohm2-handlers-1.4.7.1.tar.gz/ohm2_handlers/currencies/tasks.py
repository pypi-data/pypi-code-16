from __future__ import absolute_import
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from ohm2_handlers import utils as h_utils
from . import models as currencies_models
import time, random, datetime


@shared_task()
def currencies_test_task():
	pass