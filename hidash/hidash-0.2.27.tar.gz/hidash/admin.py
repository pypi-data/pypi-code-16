from django.contrib import admin
import models
from django.core import urlresolvers
from forms import ScheduledReportForm

class ChartMetricInlineAdmin(admin.TabularInline):
    model = models.ChartMetric
    fk_name = 'chart'
    extra = 1


class ChartAuthPermissionInlineAdmin(admin.TabularInline):
    model = models.ChartAuthPermission
    fk_name = 'chart'
    extra = 1


class ChartAuthGroupInlineAdmin(admin.TabularInline):
    model = models.ChartAuthGroup
    fk_name = 'chart'
    extra = 1


class ChartGroupInlineAdmin(admin.TabularInline):
    model = models.ChartGroup
    extra = 1


class ChartAdmin(admin.ModelAdmin):
    list_display = ('name', 'library', 'chart_type', 'priority', 'grid_width',
                    'height', 'group')
    inlines = [
        ChartMetricInlineAdmin, ChartAuthPermissionInlineAdmin,
        ChartAuthGroupInlineAdmin, ChartGroupInlineAdmin
    ]

    def group(self, instance):
        chart_group = models.ChartGroup.objects.filter(chart=instance.id)
        chart_groups = ''
        if chart_group:
            for group in chart_group:
                chart_groups = chart_groups + group.group.name + ', '
            return chart_groups[:-2]
        else:
            return "No group assigned"


class ChartParameterAdmin(admin.TabularInline):
    model = models.ChartParameter


class GroupAdmin(admin.ModelAdmin):
    list_display = ['name']
    inlines = [ChartParameterAdmin]


class ReportRecipientsAdmin(admin.TabularInline):
    model = models.ReportRecipients


class ScheduledReportParamAdmin(admin.TabularInline):
    model = models.ScheduledReportParam


class ScheduledReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'group','get_recipients', 'get_parameters')
    fields = ('group','template','email_subject','email_message','cron_expression')
    inlines = [
        ScheduledReportParamAdmin,
        ReportRecipientsAdmin
    ]
    form = ScheduledReportForm

    def get_parameters(self, model):
        param_list = '<ul>'
        for param in model.scheduledreportparam_set.all().values_list('parameter_name', 'parameter_value'):
            param_list = param_list + '<li>' + param[0] + ': ' + param[1] + '</li>'
        param_list = param_list + '</ul>'
        return param_list

    def get_recipients(self, model):
        recipients = model.reportrecipients_set.all().values_list('email_address', flat=True)
        if not recipients:
            return 'No recipients added'
        recipient_list = ''
        for recipient in recipients:
            recipient_list = recipient_list + recipient + ', '
        return recipient_list[:-2]

    get_recipients.short_description = 'Recipients'
    get_parameters.short_description = 'Parameters and value'
    get_parameters.allow_tags = True
    get_recipients.allow_tags = True

admin.site.register(models.ScheduledReport, ScheduledReportAdmin)
admin.site.register(models.Chart, ChartAdmin)
admin.site.register(models.Group, GroupAdmin)



