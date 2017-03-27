from django.contrib import admin
from .models import DJANGO_MODELS_REGISTRY


for model in DJANGO_MODELS_REGISTRY.values():
    admin.site.register(model)