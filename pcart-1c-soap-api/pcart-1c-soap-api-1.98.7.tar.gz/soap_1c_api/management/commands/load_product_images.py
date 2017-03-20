# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    args = ''
    help = 'Fill database of delivery_pages'

    def handle(self, *args, **options):
        from tasks.models import Job
        from soap_1c_api.jobs import product_load_images
        from datetime import datetime
        if Job.objects.filter(
                name='soap_1c_api.jobs.product_load_images',
                duty=5):
            return
        jobs = Job.objects.filter(
            name='soap_1c_api.jobs.product_load_images',
            duty=1
        ).order_by('added')
        if jobs:
            job = jobs[0]
            job.duty = 5
            job.started = datetime.now()
            job.save()
            errors = product_load_images(*job.args, **job.kwargs)
            if errors:
                job.result = errors
            job.duty = 9
            job.executed = datetime.now()
            job.save()
