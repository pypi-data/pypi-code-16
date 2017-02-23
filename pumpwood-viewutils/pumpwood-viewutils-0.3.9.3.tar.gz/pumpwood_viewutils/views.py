#!/usr/bin/python
# -*- coding: utf-8 -*-
import inspect
import pandas
import numpy

from functools import wraps
from rest_framework.exceptions import PermissionDenied

from django.conf   import settings
from django.db     import models

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404

from pumpwood_communication.exceptions import PumpWoodException \
                                            , PumpWoodForbidden

from rest_framework import viewsets, status
from rest_framework.response import Response

from .query import filter_by_dict
from .serializers import SerializerObjectActions

from .rest_function import RestFunctionSerializer


def save_serializer_instance(serializer_instance):
    is_valid = serializer_instance.is_valid()
    if is_valid:
        return serializer_instance.save()
    else:
        raise PumpWoodException(serializer_instance.errors)


def validate_permitions(view):
    @wraps(view)
    def wrapper(self, request, *args, **kwargs):
        if request.user is None:
            raise NotAuthenticated()

        if view.__name__ in ['list', 'list_search_options']:
            permition = self.service_model._meta.app_label + '.' + self.service_model.__name__.lower() + '.' + self.permissions['list']
            if not request.user.has_perm( permition ):
                raise PermissionDenied('User can not list ' + self.service_model.__name__ + ' objects.')

        if view.__name__ in ['list_without_pag', 'pivot']:
            permition = self.service_model._meta.app_label + '.' + self.service_model.__name__.lower() + '.' + self.permissions['list-without-pag']
            if not request.user.has_perm( permition ):
                raise PermissionDenied('User can not list without pagination '  + self.service_model.__name__ + ' objects.')

        if view.__name__ in ['retrieve']:
            permition = self.service_model._meta.app_label + '.' + self.service_model.__name__.lower() + '.' + self.permissions['retrive']
            if not request.user.has_perm(permition):
                raise PermissionDenied('User can not retrive '  + self.service_model.__name__ + ' objects.')

        if view.__name__ in ['save', 'list_options']:
            permition = self.service_model._meta.app_label + '.' + self.service_model.__name__.lower() + '.' + self.permissions['save']
            if not request.user.has_perm(permition):
                raise PermissionDenied('User can not save '  + self.service_model.__name__ + ' objects.')

        if view.__name__  == 'list_actions':
            permition = self.service_model._meta.app_label + '.' + self.service_model.__name__.lower() + '.' + self.permissions['action']
            if not request.user.has_perm( permition ):
                raise PermissionDenied('User can not apply actions over '  + self.service_model.__name__ + ' objects.')

        if view.__name__ == 'execute_action':
            permition = self.service_model._meta.app_label + '.' + self.service_model.__name__.lower() + '.' + self.permissions['action'] + '.' + kwargs['action']
            if not request.user.has_perm( permition ):
                raise PermissionDenied('User can not apply action ' + kwargs['action'] +' over '  + self.service_model.__name__ + ' objects.')
        return view(self, request, *args, **kwargs)
    return wrapper
        

class PumpWoodRestService(viewsets.ViewSet):
    '''
        Basic View-Set for pumpwood rest end-points
    '''
    list_serializer = None
    retrive_serializer = None
    service_model = None
    permissions = {'list'            : 'list'
                  ,'list-without-pag': 'list-without-pag'
                  ,'retrive'         : 'retrive'
                  ,'save'            : 'save'
                  ,'action'          : 'action'}

    @validate_permitions
    def list(self, request):
        '''
            View function to list objects. number of objects are limited by settings.REST_FRAMEWORK['PAGINATE_BY']. To get next page, use exclude_dict['pk__in': [list of the received pks]]
            to get more objects.

            Use to limit the query .query.filter_by_dict function.

            :param request.data['filter_dict']: Dictionary passed as objects.filter(**filter_dict)
            :type request.data['filter_dict']: dict
            :param request.data['exclude_dict']: Dictionary passed as objects.exclude(**exclude_dict)
            :type request.data['exclude_dict']: dict
            :param request.data['ordering_list']: List passed as objects.order_by(*ordering_list)
            :type request.data['ordering_list']: list
            :return: A list of objects using list_serializer
        '''
        PAGINATE_BY = settings.REST_FRAMEWORK.get('PAGINATE_BY')
        if self.list_serializer is None:
            raise PumpWoodForbidden('List not defined to ' + self.__class__.__name__ + ' rest service')

        arg_dict = {'query_set': self.service_model.objects.all()}
        arg_dict.update(request.data)
        query_set = filter_by_dict(**arg_dict)[:PAGINATE_BY]
        return Response(self.list_serializer(query_set, many=True).data)

    @validate_permitions
    def list_without_pag(self, request):
        '''
            View function to list objects. Basicaley the same of list, but without limitation by settings.REST_FRAMEWORK['PAGINATE_BY'].

            :param request.data['filter_dict']: Dictionary passed as objects.filter(**filter_dict)
            :type request.data['filter_dict']: dict
            :param request.data['exclude_dict']: Dictionary passed as objects.exclude(**exclude_dict)
            :type request.data['exclude_dict']: dict
            :param request.data['ordering_list']: List passed as objects.order_by(*ordering_list)
            :type request.data['ordering_list']: list
            :return: A list of objects using list_serializer

            .. note::
                Be careful with the number of the objects that will be retrieved
        '''
        if self.list_serializer is None:
            raise PumpWoodForbidden('List not defined to ' + self.__class__.__name__ + ' rest service')

        arg_dict = {'query_set': self.service_model.objects.all()}
        arg_dict.update(request.data)
        query_set = filter_by_dict(**arg_dict)
        return Response(self.list_serializer(query_set, many=True).data)

    @validate_permitions
    def retrieve(self, request, pk=None):
        '''
            Retrieve view, uses the retrive_serializer to return object with pk.

            :param int pk: Object pk to be retrieve
            :return: The representation of the object passed by self.retrive_serializer
            :rtype: dict
        '''
        if self.retrive_serializer is None:
            raise PumpWoodForbidden('Retrive not defined to ' + self.__class__.__name__ + ' rest service')

        obj = get_object_or_404(self.service_model, pk=pk)
        return Response(self.retrive_serializer(obj, many=False).data)

    @validate_permitions
    def delete(self, request, pk=None):
        '''
            Delete view, it is not implemented. Coder must do it.

            :param int pk: Object pk to be retrieve
            :raise PumpWoodForbidden: 'Delete case has not been implemented' if not implemented.
        '''
        raise PumpWoodForbidden('Delete case has not been implemented')

    @validate_permitions
    def save(self, request):
        '''
            Saves and updates object acording to request.data. Object will be updated if request.data['pk'] is not None.

            :param dict request.data: Object representation as self.retrive_serializer
            :raise PumpWoodException: 'Object model class diferent from {service_model} : {model_class}' request.data['model_class'] not the same as self.service_model.__name__
        '''
        request_data = request.data

        if request_data.get('model_class') != self.service_model.__name__:
            raise PumpWoodException('Object model class diferent from {service_model} : {model_class}'.format(
                service_model=self.service_model.__name__, model_class=request_data.get('model_class')))

        data_pk = request_data.get('pk')
        saved_obj = None
        # update
        if data_pk:
            data_to_update = self.service_model.objects.get(pk=data_pk)
            serializer = self.retrive_serializer(data_to_update, data=request_data, context={'request': request})
            saved_obj = save_serializer_instance(serializer)
            response_status = status.HTTP_200_OK
        # save
        else:
            serializer = self.retrive_serializer(data=request_data, context={'request': request})
            saved_obj = save_serializer_instance(serializer)
            response_status = status.HTTP_201_CREATED
        #Overhead, serializando e deserializando o objecto
        return Response( self.retrive_serializer(saved_obj).data, status=response_status )

    @validate_permitions
    def list_actions(self, request):
        '''
            List model actions flaged with @rest_function wrapper. It returns the list of the actions and its descriptions.

            :returns: A list of actions descriptions using .serializer.SerializerObjectActions
            :rtype: list of dictionaries
        '''
        method_dict = dict(inspect.getmembers(self.service_model, predicate=inspect.ismethod))
        action_objs = []
        for method in method_dict.keys():
            function = method_dict[method]
            if getattr(function, 'rest_function', False):
                action_objs.append(function.action_obj)
        #
        return Response(SerializerObjectActions(action_objs, many=True).data)

    @validate_permitions
    def execute_action(self, request, action, pk=None):
        '''
            Execute action over objects defined by the pk.

            :param str action: The action that will be performed
            :param int pk: Pk of the object that the action will be performed over. If it is a staic action, pk must be None
            :param dict request.data: Parameters to used on the action
            
            :return: A dictionary {'result': action result, 'action': action name, 'parameters': parameters used in the action, 'obj': the serialized object that was used in the action }
            :rtype: dict

            :raise PumpWoodForbidden: 'There is no method {action} in rest actions for {class_name}' if action not found
        '''
        request_data = request.data
        method_dict = dict(inspect.getmembers(self.service_model, predicate=inspect.ismethod))

        rest_action_names = []
        for method in method_dict.keys():
            function = method_dict[method]
            if getattr(function, 'rest_function', False):
                rest_action_names.append(method)

        if action in rest_action_names:
            obj = None
            function = None
            if pk is not None:
                obj = self.service_model.objects.get(pk=pk)
                function = getattr(obj, action)
            else:
                function = getattr(self.service_model, action)

            result     = RestFunctionSerializer.run_rest_function(function=function, request=request)
            action     = SerializerObjectActions( function.action_obj, many=False ).data
            parameters = request_data
            
            obj_dict = None
            if obj is not None:
                obj_dict = self.list_serializer(obj).data
            return Response({'result':result, 'action':action, 'parameters':parameters, 'obj': obj_dict})

        else:
            raise PumpWoodForbidden('There is no method {action} in rest actions for {class_name}'.format(action=action,
                                                                                                          class_name=self.service_model.__name__))

    @validate_permitions
    def list_search_options(self, request):
        '''
            Return options to be used in list funciton.

            :return: Dictionary with options for list parameters
            :rtype: dict

            .. note::
                Must be implemented
        '''
        raise PumpWoodForbidden('Search options not implemented')

    @validate_permitions
    def list_options(self, request):
        '''
            Return options for object update acording its partial data.

            :param dict request.data: Partial object data.
            :return: A dictionary with options for diferent objects values
            :rtype: dict

            .. note::
                Must be implemented
        '''
        raise PumpWoodForbidden('Object options not implemented')


class PumpWoodDataBaseRestService(PumpWoodRestService):
    '''
        This view extends PumpWoodRestService, including pivot function.
    '''
    model_variables = []
    'Specify which model variables will be returned in pivot. Line index are the model_variables - columns (function pivot parameter) itens.'
    
    @validate_permitions
    def pivot(self, request):
        '''
            Pivot QuerySet data acording to columns selected, and filters passed.

            :param request.data['filter_dict']: Dictionary passed as objects.filter(**filter_dict)
            :type request.data['filter_dict']: dict
            :param request.data['exclude_dict']: Dictionary passed as objects.exclude(**exclude_dict)
            :type request.data['exclude_dict']: dict
            :param request.data['ordering_list']: List passed as objects.order_by(*ordering_list)
            :type request.data['ordering_list']: list
            :param request.data['columns']: Variables to be used as pivot collumns
            :type request.data['columns']: list
            :param request.data['format']: Format used in pandas.DataFrame().to_dict()
            :type request.data['columns']: str
            
            :return: Return database data pivoted acording to columns parameter
            :rtyoe: panas.Dataframe converted to disctionary
        '''
        columns = request.data.get('columns', [])
        format  = request.data.get('format', 'list')

        if type(columns) != list:
            raise PumpWoodException('Columns must be a list of elements.')

        if len(set(columns) - set(self.model_variables)) != 0:
            raise PumpWoodException('Column chosen as pivot is not at model variables')

        index = list(set(self.model_variables) - set(columns))
        filter_dict = request.data.get('filter_dict', {})
        exclude_dict = request.data.get('exclude_dict', {})
        ordering_list = request.data.get('ordering_list', {})

        arg_dict = {'query_set': self.service_model.objects.all(),
                    'filter_dict': filter_dict,
                    'exclude_dict': exclude_dict,
                    'ordering_list': ordering_list}
        query_set = filter_by_dict(**arg_dict)

        filtered_objects_as_list = list( query_set.values_list( *(self.model_variables + ['value']) ) )
        melted_data = pandas.DataFrame(filtered_objects_as_list, columns=self.model_variables + ['value'])

        if len(columns) == 0:
            return Response( melted_data.to_dict( format ) )

        if melted_data.shape[0] == 0:
            return Response({})
        else:
            pivoted_table = pandas.pivot_table(melted_data,
                                               values='value',
                                               index=index,
                                               columns=columns,
                                               aggfunc = lambda x: tuple(x)[0] )
        
            return Response( pivoted_table.reset_index().to_dict( format ) )