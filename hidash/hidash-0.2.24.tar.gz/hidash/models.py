from django.db import models
from datetime import datetime
from croniter import croniter
from django import forms
from django.conf import settings
from django.core.files.storage import default_storage
import os


CHART_WIDTHS = ((1, '1'), (2, '2'), (3, '3'), (4, '4'),
                (5, '5'), (6, '6'), (7, '7'), (8, '8'),
                (9, '9'), (10, '10'), (11, '11'), (12, '12'))

CHARTING_LIBRARIES = ((0, 'highcharts'),
                      (1, 'googlechart'))


PARAMETER_TYPES = ((0, 'dropdown'),
                   (1, 'dateTime'),
                   (2, 'dateRange'),
                   (3, 'periodicDatePicker'))


if hasattr(settings, 'HIDASH_SETTINGS') and 'storage' in settings.HIDASH_SETTINGS:	
    storage = settings.HIDASH_SETTINGS['storage']()
else:
    storage = default_storage

def get_storage_path(instance, file):
    if hasattr(settings, 'HIDASH_SETTINGS') and 'storage_path_provider' in settings.HIDASH_SETTINGS:
        if hasattr(settings, 'ENV'):
        	path =  os.path.join('./', settings.ENV, settings.HIDASH_SETTINGS['storage_path_provider']())
        else:
    	    path = os.path.join('./', settings.HIDASH_SETTINGS['storage_path_provider']())
    else:
        path = './'
    return path + '/' + file

class Chart(models.Model):
    '''
    Holds the configuration of a chart
    '''
    name = models.CharField(max_length=255, unique=True)
    library = models.IntegerField(choices=CHARTING_LIBRARIES, null=True,
                                  blank=True)
    dimension = models.CharField(max_length=255, null=True, blank=True)
    # FIXME: Remove separator field and add associate multiple dimentions with a charts
    separator = models.CharField(max_length=128, null=True, blank=True)
    chart_type = models.CharField(max_length=15, null=True, blank=True)
    query = models.TextField(max_length=10000)
    description = models.CharField(max_length=2000, null=True, blank=True)
    grid_width = models.IntegerField(choices=CHART_WIDTHS, null=True,
                                     blank=True)
    height = models.CharField(max_length=20, null=True, blank=True)
    priority = models.PositiveIntegerField(null=True, blank=True)


    def __unicode__(self):
        return self.name


class Group(models.Model):
    '''
    Holds a group name and the template doc associated to it
    '''
    name = models.CharField(max_length=128)
    template = models.FileField(upload_to=get_storage_path, blank=True, null=True, storage=storage)

    def __unicode__(self):
        return str(self.name)


class ChartGroup(models.Model):
    '''
    Holds the Group names for grouping multiple charts under that group
    '''
    group = models.ForeignKey(Group)
    chart = models.ForeignKey(Chart)

    def __unicode__(self):
        return str(self.id)


class ChartParameter(models.Model):
    parameter_name = models.CharField(max_length=128, default='', blank=True)
    parameter_type = models.IntegerField(choices=PARAMETER_TYPES, null=True,
                                         blank=True)
    priority = models.PositiveIntegerField(null=True, blank=True)
    grid_width = models.IntegerField(choices=CHART_WIDTHS, null=True,
                                     blank=True)
    group = models.ForeignKey(Group)


class ChartMetric(models.Model):
    '''
    One to many mapping to hold the metrics of a chart
    '''
    chart = models.ForeignKey(Chart, related_name='chart')
    metric = models.CharField(max_length=128)

    def __unicode__(self):
        return self.metric


class ChartAuthGroup(models.Model):
    '''
    One to many mapping to hold the chart_groups permitted to view the chart
    '''
    chart = models.ForeignKey(Chart)
    auth_group = models.CharField(max_length=50)

    def __unicode__(self):
        return self.auth_group


class ChartAuthPermission(models.Model):
    '''
    One to many mapping to hold the needed permissions to view the chart
    '''
    chart = models.ForeignKey(Chart)
    permission = models.CharField(max_length=50)

    def __unicode__(self):
        return self.permission


class ScheduledReport(models.Model):
    '''
    It will contain the parameters for the reports and reports recipients
    '''
    group = models.ForeignKey(Group, default=1)
    template = models.FileField(upload_to=get_storage_path, blank=True, null=True, storage=storage)
    email_message = models.TextField(max_length=10000, default="")
    email_subject = models.CharField(max_length=1000, default="")
    last_run_at = models.DateTimeField(null=True, blank=True)
    next_run_at = models.DateTimeField(null=True, blank=True)
    cron_expression = models.CharField(max_length=100, default="")

    def save(self, *args, **kwargs):
        if not self.last_run_at:
            self.last_run_at = datetime.now()
        base = self.last_run_at
        iter = croniter(self.cron_expression, base)
        self.next_run_at = iter.get_next(datetime)
        super(ScheduledReport, self).save(*args, **kwargs)


class ReportRecipients(models.Model):
    '''
    It will store all the recipients for a given group of reports
    '''
    email_address = models.CharField(max_length=512, default='', blank=True)
    report = models.ForeignKey(ScheduledReport)


class ScheduledReportParam(models.Model):
    '''
    It will store the query parameters for every schedule report
    '''
    parameter_name = models.CharField(max_length=128, default='', blank=True)
    is_parameter_value_sql_function = models.BooleanField(default=False)
    parameter_value = models.CharField(max_length=128, default='', blank=True)
    scheduled_report = models.ForeignKey(ScheduledReport)



