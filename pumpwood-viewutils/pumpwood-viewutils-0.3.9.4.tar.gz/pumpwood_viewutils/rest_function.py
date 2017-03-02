#!/usr/bin/python
# -*- coding: utf-8 -*-
import inspect
from pumpwood_communication.exceptions import PumpWoodException

from django.core.exceptions import ImproperlyConfigured
from .serializers           import SerializerObjectActions

class RestAction:
  '''
    Class responsible for keeping the instructions to expose an action as a rest service. This class is also used to keep information
    about the function that will be exposed so it can be retrived and passed to front end when it is serialized.
    
    It is used inside @rest_function wrapper.

    :param function fn: Function to extract name and class
    :param str model_class: Name of the model of the function that will be exposed
    :param str icon: Path to the icon of the function.
    :param str description: String to describe action.
    :param dict validation_dict: A dictonary that indicates validations that will be performed when data is received
    :param bool static: Tell if the function is static and not associated to an specific object
    :param dict parameters: A dictionary containing the description of the parameters necessary to run the fucntion
    :param dict opt_parameters: A dictionary containing the description of the optional parameters to run the fucntion
    :param dict return_dict: A dictionary containing the description of what the function will return
    :param string request_user: A string telling if the request user will be used as as argument in function. None no, a string name of the kwargs key that will hold user name
  '''

  def __init__(self, fn, model_class, icon, description, validation_dict, static, parameters, opt_parameters, return_dict, request_user=None):
    def check_parameter_dict(par_dict, transformation_dict, error_name):
      for k in par_dict.keys():
        if not set(par_dict[k].keys()) == set(['type', 'many']):
          raise KeyError('{function_name}: Transformation dict {error_name} entry {par_dict_key} does not have type and many keys'.format(function_name=fn.__name__, error_name=error_name, par_dict_key=k))

        if par_dict[k]['type'] not in transformation_dict:
          raise KeyError('{function_name}: Transformation dict {error_name} type entry {par_dict_key} does not have {trans_key} transformation'.format(function_name=fn.__name__, error_name=error_name, par_dict_key=k, trans_key=par_dict[k]['type']))
        
        if type(par_dict[k]['many']) != bool:
          raise TypeError('{function_name}: Transformation dict {error_name} type entry {par_dict_key} many is not bool'.format(function_name=fn.__name__, error_name=error_name, par_dict_key=k))

    args_in_function_original = inspect.getargspec(fn).args
    args_in_function          = []
    for i in range(0, len(args_in_function_original)):
      if args_in_function_original[i] not in ['self', 'cls', request_user]:
        args_in_function.append( args_in_function_original[i] )
    
    if set(args_in_function) != set( list(parameters.keys()) + list(opt_parameters.keys()) ):
      not_in_dicts = set(args_in_function) - set( list(parameters.keys()) + list(opt_parameters.keys()) )
      not_in_fun   = set( list(parameters.keys()) + list(opt_parameters.keys()) ) - set(args_in_function)
      raise Exception('Function {function_name} arguments and parameters + opt_parameters keys are not the same:\nArgs not in dicts: {not_in_dicts};\nArgs not in function pars: {not_in_fun}'.format(function_name=fn.__name__, not_in_dicts=not_in_dicts, not_in_fun=not_in_fun))


    self.icon            = icon
    self.modelclass      = model_class
    self.action_name     = fn.__name__
    self.description     = description
    self.validation_dict = validation_dict
    self.parameters      = parameters
    self.opt_parameters  = opt_parameters
    self.return_dict     = return_dict
    self.static          = static
    self.request_user    = request_user


class SerializerDictionary():
  '''
    Class used to store how the function variables will be serialized.
  '''
  __serializer_in_dict  = {}
  'Dictionary with the diferent serialization options for recevied data'
  __serializer_out_dict = {}
  'Dictionary with the diferent serialization options for sending data'

  @classmethod
  def add_serializer_in(cls, var_type, one_lambda, many_lambda):
    '''
      Add a receiving data serializer
      
      :param var_type str: String corresponding to a type that will be later used in @rest_function parameters or opt_parameters definition
      :param one_lambda function: Function defining how the income data will be converted to Python simple or complex (Model Objects, pandas.DataFrame, ...), when data is not many (list)
      :param many_lambda function: Function defining how the income data will be converted to Python simple objects (list, dict, int, ...)
      :return: None
    '''
    cls.__serializer_in_dict[var_type] = {'one_lambda': one_lambda, 'many_lambda': many_lambda}

  @classmethod
  def add_serializer_out(cls, var_type, one_lambda, many_lambda):
    '''
      Add a sending data serializer
      
      :param var_type str: String corresponding to a type that will be later used in @rest_function parameters or opt_parameters definition
      :param one_lambda function: Function defining how the sending data will be converted to Python simple or complex (Model Objects, pandas.DataFrame, ...), when data is not many (list)
      :param many_lambda function: Function defining how the sending data will be converted to Python simple objects (list, dict, int, ...)
      :return: None
    '''
    cls.__serializer_out_dict[var_type] = {'one_lambda': one_lambda, 'many_lambda': many_lambda}    

  @classmethod
  def get_in_serializer(cls, var_type):
    '''
      Check if in serializer is avaible for var_type

      :param var_type str: String corresponding to variable type
      :return: var_type in serializer
      :raise PumpWoodException: If in serializer for var_type have not been added
    '''
    serializer = cls.__serializer_in_dict.get(var_type, None)
    if serializer is not None:
      raise PumpWoodException( 'Variable type in serializer not found: var_type=' + var_type )
    return serializer

  @classmethod
  def serialize_in(cls, var_type, data):
    '''
      Serialize income data acording to its var_type

      :param var_type str: var_type of the income data
      :param data variable: Data to be serialized
      :return: Data serialized acording to __serializer_in_dict[var_type]
    '''
    serializer = None
    if type(data) == list:
      serializer = cls.get_in_serializer(var_type).get('many_lambda', None)
    else:
      serializer = cls.get_in_serializer(var_type).get('one_lambda', None)

    return serializer(data)

  @classmethod
  def get_out_serializer(cls, var_type):
    '''
      Check if out serializer is avaible for var_type

      :param var_type str: String corresponding to variable type
      :return: var_type out serializer
      :raise PumpWoodException: If out serializer for var_type have not been added
    '''
    serializer = cls.__serializer_out_dict.get(var_type, None)
    if serializer is not None:
      raise PumpWoodException( 'Variable type out serializer not found: var_type=' + var_type )
    return serializer

  @classmethod
  def serialize_out(cls, var_type, data):
    '''
      Serialize sending data acording to its var_type

      :param var_type str: var_type of the sending data
      :param data variable: Data to be serialized
      :return: Data serialized acording to __serializer_out_dict[var_type]
    '''
    serializer = None
    if type(data) == list:
      serializer = cls.get_out_serializer(var_type).get('many_lambda', None)
    else:
      serializer = cls.get_out_serializer(var_type).get('one_lambda', None)
    
    if serializer is None:
      raise PumpWoodException( 'It is not possible to find serializer to output ' + var_type )

    return serializer(data)


class RestFunctionSerializer(object):
  '''
    Wraps SerializerDictionary and taget function to run the function and validates if all necessary parameters were passed

    :param function function: Function that will be used to process request income data
    :param request: Income Django request
    :return: Function results in serializable simples Python objects (int, list, dict, ...)
  '''
  @classmethod
  def run_rest_function(cls, function, request):
    action_obj = function.action_obj
    function_kwargs = cls.fun_args_parser(action_obj=action_obj, request=request)
    resp = function(**function_kwargs)
    return cls.result_parser(action_obj=action_obj, results=resp)


  @staticmethod
  def fun_args_parser(action_obj, request):
    '''
      Uses function action_obj to transform request.data so it can be used to run the function
      
      :param action_obj RestAction: action_obj associated with the function by rest_function wrapper
      :param request: Inconme Django request
      :return: a dictionary of the function kwargs
      :rtype: dict
    '''
    parameter_dict = request.data

    response_dict = {}
    action_pars__keys     = action_obj.parameters.keys()
    opt_action_pars__keys = action_obj.opt_parameters.keys()
    parameter_dict__keys  = parameter_dict.keys()

    have_all_needed = list((set(action_pars__keys) - set(parameter_dict__keys)) - set(opt_action_pars__keys) )
    have_extra      = list(set(action_pars__keys) - set(parameter_dict__keys + opt_action_pars__keys))

    pump_text  = ""
    raise_pump = False
    if len(have_all_needed) != 0:
      joined = ", ".join(have_all_needed)
      pump_text = "Parameter missing to perform action: " + joined + "\n"
      raise_pump = True

    if len(have_extra) > 0:
      joined = ", ".join(have_extra)
      pump_text  = "More parameters needed then necessary to perform action: " + joined + "\n"
      raise_pump = True

    if raise_pump:
      raise PumpWoodException(pump_text)

    for k in parameter_dict.keys():
      if k in action_pars__keys:
        var_type = action_obj.parameters[k]['type']
        many     = action_obj.parameters[k]['many']
      else:
        var_type = action_obj.opt_parameters[k]['type']
        many     = action_obj.opt_parameters[k]['many']

      response_dict[k] = SerializerDictionary.serialize_in(var_type=var_type, data=parameter_dict[k])

    if action_obj.request_user is not None:
     response_dict[action_obj.request_user] = request.user
    
    return response_dict

  @staticmethod
  def result_parser(action_obj, results):
    '''
      Uses function action_obj to transform function results to python serializible simple functions
      
      :param action_obj RestAction: action_obj associated with the function by rest_function wrapper
      :param request: Inconme Django request
      :return: function result in serializible objects (int, list, dict, ...)
    '''
    type_obj_result     = type(results)
    action_keys         = action_obj.return_dict.keys()

    to_return = None
    if type_obj_result == dict:
      #Resposta da função como um dicionário
      to_return = {}

      obj_result_keys = results.keys()
      have_all_needed  = list(set(action_keys) - set(obj_result_keys))
      if have_all_needed != []:
        raise TypeError('Keys in action result dict and not in object result: ' + str(have_all_needed))

      more_than_needed = list(set(obj_result_keys) - set(action_keys))
      if more_than_needed != []:
        raise TypeError('Keys in object result and not in action result dict: ' + str(more_than_needed))

      for obj_k in obj_result_keys:
        var_type = action_obj.return_dict[obj_k]['type']
        many = action_obj.return_dict[obj_k]['many']
        to_return[ obj_k ] = SerializerDictionary.serialize_out(var_type=var_type, data=results[obj_k])

    else:
      if len( action_keys ) > 1:
        raise TypeError('More than one key in action return dict and function return is not a dict.')

      if action_keys[0] != 'flat':
        raise TypeError('Result type not dict and return_dict dict with one key but not "flat"')

      var_type = action_obj.return_dict[ action_keys[0] ]['type']
      to_return = SerializerDictionary.serialize_out(var_type=var_type, data=results)

    return to_return



def rest_function(model_class, icon, description, validation_dict, static, parameters, opt_parameters, return_dict, request_user=None):
  '''
      Function Wrapper defining rest caracteristics to be used for income data a
      
      Usage:

      .. code-block:: python

          class ExampleModel(models.Model):
            ...

            @rest_function(model_class='ExampleModel'
                         , icon='example_icon'
                         , description='A great description for a example function'
                         , validation_dict={}
                         , static=False
                         , parameters={ 'arg1': {'type': 'dict', 'many': False}
                                      , 'arg2': {'type': 'int', 'many': True}
                                      , 'arg3': {'type': 'PandasDataframe', 'many': True} }
                         , opt_parameters={ 'arg4': {'type': 'bool', 'many': False}
                                          , 'arg5': {'type': 'int', 'many': False}
                                          , 'arg6': {'type': 'str', 'many': True} }
                         , return_dict={ 'return1': {'type': 'int', 'many': False}
                                       , 'return2': {'type': 'str', 'many': False}
                                       , 'return3': {'type': 'bool', 'many': True} }
                         , request_user='user')
            def example_function(self, user, arg1, arg2, arg3, arg4=False, arg5=5, arg6=['apple', 'orange', 'pineapple']):
              ...
              return {'return1': 1, 'return2': 'Chubaca', 'return3': [True, False, True, True]}

            @rest_function(model_class='ExampleModel'
                         , icon='example_icon'
                         , description='A great description for a example function'
                         , validation_dict={}
                         , static=False
                         , parameters={ 'arg1': {'type': 'str', 'many': False} }
                         , opt_parameters={}
                         , return_dict={ 'flat': {'type': 'pandas.DataFrame', 'many': True} }
                         , request_user=None)
            @classmethod
            def example_cls_function(cls, arg1):
              ...
              return [ pandas.DataFrame(data_set1), pandas.DataFrame(data_set2) ]



      :param action_obj RestAction: action_obj associated with the function by rest_function wrapper
      :param request: Inconme Django request
      :return: function result in serializible objects (int, list, dict, ...)
      :raise par_dict: 
      :raise KeyError: Transformation dict {error_name} entry {par_dict_key} does not have type and many keys' if parameter dict does not have type and many keys
      :raise KeyError: Transformation dict {error_name} entry {par_dict_key} does not have type and many keys'
      :raise TypeError: 
      :raise Exception: 
    '''
  def wrap(f):
    f.rest_function = True
    f.action_obj = RestAction(fn              = f
                            , model_class     = model_class
                            , icon            = icon
                            , description     = description
                            , validation_dict = validation_dict
                            , static          = static
                            , parameters      = parameters
                            , opt_parameters  = opt_parameters
                            , return_dict     = return_dict
                            , request_user    = request_user)
    return f
  return wrap