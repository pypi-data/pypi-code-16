from django.db import models
from django.conf import settings

class SiteSetting(models.Model):
    organization = models.CharField(max_length=75)
    description = models.CharField(max_length=512, null=True)
    background = models.ImageField(upload_to='background', null=True,
                                   blank=True)

class SidebarLink(models.Model):
    url = models.CharField(max_length=75)
    name = models.CharField(max_length=75)
    settings = models.ForeignKey(SiteSetting, on_delete=models.CASCADE)

# These will not be available on Mobile
class TitlebarLink(models.Model):
    url = models.CharField(max_length=75)
    name = models.CharField(max_length=75)
    settings = models.ForeignKey(SiteSetting, on_delete=models.CASCADE)

class GlobalTemplateSettings():
    def __init__(self, allowBackground):
        self.allowBackground = allowBackground
        self.background = None
        try:
            site_settings = SiteSetting.objects.get(pk=1)
            self.organization = site_settings.organization
            self.description = site_settings.description
            self.background = site_settings.background if self.allowBackground else None
        except SiteSetting.DoesNotExist:
            self.organization = "My Organization"
            self.description = "An organization description will need to be set up in \
            the admin panel"
        try:
            self.sidebar_links = SidebarLink.objects.all()
        except SidebarLink.DoesNotExist:
            self.sidebar_links = None
        try:
            self.titlebar_links = TitlebarLink.objects.all()
        except TitlebarLink.DoesNotExist:
            self.titlebar_links = None

    def settings_dict(self):
        return {
            'background': self.background,
            'description': self.description,
            'organization': self.organization,
            'sidebar_links': self.sidebar_links,
            'titlebar_links': self.titlebar_links,
        }
