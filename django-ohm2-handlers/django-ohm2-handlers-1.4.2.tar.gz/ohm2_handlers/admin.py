from django.contrib import admin
from . import models


class AuthorAdmin(admin.ModelAdmin):
	pass

admin.site.register(models.BaseError, AuthorAdmin)
admin.site.register(models.BaseEmail, AuthorAdmin)
admin.site.register(models.Statistics, AuthorAdmin)
admin.site.register(models.LandingMessage, AuthorAdmin)
admin.site.register(models.LandingEmail, AuthorAdmin)
