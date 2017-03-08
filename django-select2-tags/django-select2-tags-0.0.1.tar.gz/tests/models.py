from django.db import models


class MyRelatedModel(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        app_label = 'tests'
        ordering = ('name',)

    def __str__(self):  # __unicode__ on Python 2
        return self.name


# TODO Make validation work with non-null fields
class MyNullableFkModel(models.Model):
    my_fk_field = models.ForeignKey(MyRelatedModel, null=True, blank=True)

    class Meta:
        app_label = 'tests'

    def __str__(self):  # __unicode__ on Python 2
        return str(self.my_fk_field)


class MyM2mModel(models.Model):
    my_m2m_field = models.ManyToManyField(MyRelatedModel)

    class Meta:
        app_label = 'tests'

    def __str__(self):  # __unicode__ on Python 2
        return str(self.my_m2m_field)
