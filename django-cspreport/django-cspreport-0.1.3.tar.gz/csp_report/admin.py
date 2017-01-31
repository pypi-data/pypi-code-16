from django.contrib import admin

from csp_report.models import CSPReport


class CSPReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'host', 'document_uri', 'blocked_uri', 'date', )
    ordering = ['-id', ]
    list_filter = ('host', 'date', )

admin.site.register(CSPReport, CSPReportAdmin)
