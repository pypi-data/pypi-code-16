from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    THEMES = (
        ('1', 'Cerulean'),
        ('2', 'Cosmo'),
        ('3', 'Cyborg'),
        ('4', 'Darkly'),
        ('5', 'Flatly'),
        ('6', 'Journal'),
        ('7', 'Lumen'),
        ('8', 'Paper'),
        ('9', 'Readable'),
        ('10', 'Sandstone'),
        ('11', 'Simplex'),
        ('12', 'Slate'),
        ('13', 'Spacelab'),
        ('14', 'Superhero'),
        ('15', 'United'),
        ('16', 'Yeti'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    theme = models.CharField(
        max_length=2, default=THEMES[0][0], choices=THEMES
    )

    class Meta:
        app_label = 'nimble'

    def theme_name(self):
        for key, name in self.THEMES:
            if key == self.theme:
                return name


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
