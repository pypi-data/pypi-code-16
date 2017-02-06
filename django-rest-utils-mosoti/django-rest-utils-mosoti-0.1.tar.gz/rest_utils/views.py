from django.shortcuts import render

# Create your views here.
from django.db import transaction
from django.utils.decorators import method_decorator
#create global transactional class mixin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


class TransactionalViewMixin(object):
    """This is a global view wrapper that provides ,
    transactions and filters
    """
    filter_backends = (DjangoFilterBackend,filters.SearchFilter,)

    def perform_destroy(self,model_object):
        """ called by generic detail view for flagging is_deleted to True.  
        """
        
        model_object.is_deleted=True
        model_object.save()
    @method_decorator(transaction.atomic)
    def dispatch(self, *args, **kwargs):
        return super(TransactionalViewMixin, self).dispatch(*args, **kwargs)