from django.db import models


class UserPixelpinAuthManager(models.Manager):
    """Manager for the UserPixelpinAuth django model."""

    class Meta:
        app_label = "pixelpin_auth_django"

    def get_pixelpin_auth(self, provider, uid):
        try:
            return self.select_related('user').get(provider=provider,
                                                   uid=uid)
        except self.model.DoesNotExist:
            return None
