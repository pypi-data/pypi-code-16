# -*- coding:utf-8 -*-
from django.db.models.query_utils import Q
from django.db.models import Manager


class ACLManager(Manager):
    def get_user_resources(self, user):
        return self.get_queryset().filter(
            Q(user=user) | Q(group__in=user.groups.all())
        ).distinct()
