from django.contrib import admin
from . import models

class AuthorAdmin(admin.ModelAdmin):
	pass

admin.site.register(models.Country, AuthorAdmin)
admin.site.register(models.Region, AuthorAdmin)
admin.site.register(models.Province, AuthorAdmin)
admin.site.register(models.Commune, AuthorAdmin)
admin.site.register(models.UserAddress, AuthorAdmin)
