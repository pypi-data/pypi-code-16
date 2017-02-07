from django.contrib import admin

from csp_report.models import CSPReport, CleanedCSPReport, CSPReportFilter
from django.core import urlresolvers
from django.template.defaultfilters import truncatechars


class CSPReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'host', 'document_uri', 'date', 'short_blocked_uri', )
    ordering = ['-id', ]
    list_filter = ('host', 'date', )

admin.site.register(CSPReport, CSPReportAdmin)


class CleanedCSPReportAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'link_to_report',
        'document_domain',
        'document_path',
        'short_document_query',
        'blocked_domain',
        'short_blocked_url',
    )
    ordering = ['-id', ]
    list_filter = ('document_domain', 'blocked_domain', 'document_path')

    def link_to_report(self, obj):
        link = urlresolvers.reverse('admin:csp_report_cspreport_change', args=[obj.report.id])
        return '<a href="{}">{}</a>'.format(link, obj.report.id)

    link_to_report.allow_tags = True


admin.site.register(CleanedCSPReport, CleanedCSPReportAdmin)


class CSPReportFilterAdmin(admin.ModelAdmin):
    ordering = ['-id', ]

admin.site.register(CSPReportFilter, CSPReportFilterAdmin)