# -*- coding: utf-8 -*-
from django.conf.urls import url
from gluttony_tw.view import restaurant
from gluttony_tw.view import order

# restaurant api
urlpatterns += [
  url(r'^api/restaurant/$', restaurant.rest_api, name='rest_api'),
  url(r'^api/restaurant/prof/$', restaurant.restaurant_prof, name='restaurant_prof'),
  url(r'^api/restaurant/list/$', restaurant.restaurant_list, name='restaurant_list'),
  url(r'^api/restaurant/menu/$', restaurant.restaurant_menu, name='restaurant_menu'),
]

# order api
urlpatterns += [
  url(r'^api/order/user/$', order.user_api, name='user_api'),
  url(r'^api/order/join$', order.join_order, name='join_order'),
  url(r'^api/order/join_order_list$', order.join_order_list, name='join_order_list'),
]
