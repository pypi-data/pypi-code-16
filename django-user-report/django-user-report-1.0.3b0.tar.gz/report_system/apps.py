from django.apps import AppConfig


class ReportSystemConfig(AppConfig):
    name = "report_system"

    def ready(self):
        from report_system.signals import signals, handlers