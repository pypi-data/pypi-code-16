from django.contrib import admin
from . import models as accounts_models

class AuthorAdmin(admin.ModelAdmin):
	pass

admin.site.register(accounts_models.Presignup, AuthorAdmin)
admin.site.register(accounts_models.Settings, AuthorAdmin)
admin.site.register(accounts_models.Keys, AuthorAdmin)
admin.site.register(accounts_models.Avatars, AuthorAdmin)
admin.site.register(accounts_models.PasswordReset, AuthorAdmin)
admin.site.register(accounts_models.ReferalCode, AuthorAdmin)
admin.site.register(accounts_models.Crypto, AuthorAdmin)
admin.site.register(accounts_models.Alias, AuthorAdmin)
