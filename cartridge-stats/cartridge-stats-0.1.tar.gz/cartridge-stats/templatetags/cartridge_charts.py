from __future__ import unicode_literals
import datetime
from django.db import connection
from django.db.models import Sum, Count
from django.utils.timezone import localtime, now
from datetime import timedelta

from mezzanine import template
from mezzanine.conf import settings

from cartridge.shop.models import Order, OrderItem

register = template.Library()

@register.inclusion_tag("admin/includes/sales_today.html", takes_context=True)
def sales_today(context):
  """
  Admin dashboard tag for cartridge to show daily sales totals. Excluding tax and shipping.
  """

  today_min = localtime(now()).replace(hour=0, minute=0, second=0, microsecond=0)
  today_max = localtime(now()).replace(hour=23, minute=59, second=59, microsecond=59)
  output = Order.objects.filter(time__range=(today_min, today_max),status__in=settings.SHOP_ORDER_STATUS_COMPLETE).aggregate(Sum('item_total'))

  context["daily_total"] = output
  context["daily_date"] = today_min

  return context

@register.inclusion_tag("admin/includes/sales_yesterday.html", takes_context=True)
def sales_yesterday(context):
  """
  Admin dashboard tag for cartridge to show daily sales totals. Excluding tax and shipping.
  """

  yesterday_min = localtime(now() + timedelta(days=-1)).replace(hour=0, minute=0, second=0, microsecond=0)
  yesterday_max = localtime(now() + timedelta(days=-1)).replace(hour=23, minute=59, second=59, microsecond=59)
  output = Order.objects.filter(time__range=(yesterday_min, yesterday_max),status__in=settings.SHOP_ORDER_STATUS_COMPLETE).aggregate(Sum('item_total'))

  context["yesterday_total"] = output
  context["yesterday_date"] = yesterday_min

  return context

@register.inclusion_tag("admin/includes/sales_past_7_days.html", takes_context=True)
def sales_past_7_days(context):
  """
  Admin dashboard tag for cartridge to show daily sales totals. Excluding tax and shipping.
  """
  week_min = localtime(now() + timedelta(days=-7)).replace(hour=0, minute=0, second=0, microsecond=0)
  week_max = localtime(now()).replace(hour=23, minute=59, second=59, microsecond=59)
  output = Order.objects.filter(time__range=(week_min, week_max),status__in=settings.SHOP_ORDER_STATUS_COMPLETE).aggregate(Sum('item_total'))

  context["week_total"] = output
  context["week_min"] = week_min
  context["week_max"] = week_max

  return context

@register.inclusion_tag("admin/includes/sales_current_month.html", takes_context=True)
def sales_current_month(context):
  """
  Admin dashboard tag for cartridge to show daily sales totals. Excluding tax and shipping.
  """
  today = localtime(now())
  output = Order.objects.filter(time__month=today.month,status__in=settings.SHOP_ORDER_STATUS_COMPLETE).aggregate(Sum('item_total'))

  context["month_total"] = output
  context["today"] = today

  return context

@register.inclusion_tag("admin/includes/sales_item_popularity.html", takes_context=True)
def popular_items(context):
  items = OrderItem.objects.values('sku','description').filter(order__status__in=settings.SHOP_ORDER_STATUS_COMPLETE).annotate(sku_count=Count('sku')).order_by('-sku_count')

  context["popular_items"] = items

  return context

@register.inclusion_tag("admin/includes/sales_item_popularity_today.html", takes_context=True)
def popular_items_today(context):
  today_min = localtime(now()).replace(hour=0, minute=0, second=0, microsecond=0)
  today_max = localtime(now()).replace(hour=23, minute=59, second=59, microsecond=59)
  items = OrderItem.objects.values('sku','description').filter(order__time__range=(today_min, today_max),order__status__in=settings.SHOP_ORDER_STATUS_COMPLETE).annotate(sku_count=Count('sku')).order_by('-sku_count')

  context["popular_items"] = items

  return context

@register.inclusion_tag("admin/includes/sales_by_month.html", takes_context=True)
def sales_by_month(context):
  month_min = localtime(now() + timedelta(days=-365)).replace(hour=0, minute=0, second=0, microsecond=0)
  truncate_date = connection.ops.date_trunc_sql('month', 'time')
  qs = Order.objects.extra({'month':truncate_date}).filter(status__in=[2,4],time__gte=month_min)
  reports = qs.values('month').annotate(Sum('item_total'),\
              Count('pk')).order_by('month')

  context["sales_by_months"] = reports

  return context
