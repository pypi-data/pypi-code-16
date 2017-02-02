from django.contrib import admin
from . import models as socialstatistics_models

class AuthorAdmin(admin.ModelAdmin):
	pass

admin.site.register(socialstatistics_models.Twitter, AuthorAdmin)
admin.site.register(socialstatistics_models.TwitterSnapshot, AuthorAdmin)
admin.site.register(socialstatistics_models.LastTwitterSnapshot, AuthorAdmin)
admin.site.register(socialstatistics_models.Facebook, AuthorAdmin)
admin.site.register(socialstatistics_models.FacebookPage, AuthorAdmin)
admin.site.register(socialstatistics_models.FacebookPageSnapshot, AuthorAdmin)
admin.site.register(socialstatistics_models.LastFacebookPageSnapshot, AuthorAdmin)
