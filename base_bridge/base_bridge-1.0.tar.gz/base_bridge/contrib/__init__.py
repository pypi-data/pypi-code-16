# coding=utf-8

"""
- Author:   
    - Maple.Liu 16/3/2 11:24 maple.liu@microfastup.com

- File  :   __init__.py.py
"""

from django.contrib import admin


class ModelAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return ['id',
                'uuid',
                'get_add_time',
                'get_update_time'] + list(super(ModelAdmin, self).get_list_display(request))
