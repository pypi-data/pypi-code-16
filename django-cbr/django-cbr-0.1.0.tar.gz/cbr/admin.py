# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import CBRCurrencyRate, CBRCurrency


class CBRCurrencyRateAdmin(admin.ModelAdmin):
    pass

admin.site.register(CBRCurrencyRate, CBRCurrencyRateAdmin)


class CBRCurrencyAdmin(admin.ModelAdmin):
    pass

admin.site.register(CBRCurrency, CBRCurrencyAdmin)
