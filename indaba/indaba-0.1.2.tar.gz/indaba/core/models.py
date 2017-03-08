from django.db import models

class BaseProposal(models.Model):
    abstract = models.TextField()
