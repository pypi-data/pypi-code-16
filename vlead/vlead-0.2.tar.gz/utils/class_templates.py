
def meta(_name):
    class cls():
        @staticmethod
        def inv(args):
            pass

    cls.__name__ = _name
    return cls
from type_utils import *
class ValueClassTemplate():

    @staticmethod
    def mk_init(type_pred):
        def fn(obj, val):
            obj.value = check_pred(type_pred)(val)
        return fn

    @staticmethod
    def mk_get():
        def fn(obj):
            return obj.value
        return fn

    @staticmethod
    def mk_eq():
        def fn(obj, other) :
            if isinstance(other, obj.__class__):
                return obj.value == other.value
            else:
                return False
        return fn

    @staticmethod
    def mk_str():
        def fn(obj):
            return str(obj.value)
        return fn

    @staticmethod
    def mk_class(_name, type_pred):
        cls = meta(_name) 
        cls.__init__ = ValueClassTemplate.mk_init(type_pred)
        cls.get = ValueClassTemplate.mk_get()
        cls.set = ValueClassTemplate.mk_init(type_pred)
        cls.__eq__   = ValueClassTemplate.mk_eq()
        cls.__str__  = ValueClassTemplate.mk_str()
        return cls

class ClassTemplate():

    @staticmethod
    def inv_true(obj, args):
        return True

    @staticmethod
    def mk_init(cls):
        # obj is an instance of cls
        # args is a dictionary
        def fn(obj, **args): 
            check_dict(args)
            # match arg keys with state_vars list
            check_pred(lambda a: sorted(a.keys()) == \
                           sorted(cls.sorted_state_vars))(args)

            obj.state = {}
            
            # each arg should satisfy its typecheck 
            for key, value in args.iteritems():
                cls.state_var_type_checks[key](value)

            # invariant must be true on args
            # check_inv(cls.inv,cls)args)
            if not obj.inv(args):
                raise TypeError("invariant for class %s violated for init args %s" %(cls.__name__, args))

            # initialize the state
            for key, value in args.iteritems():
                obj.state[key] = value


            if cls.is_persistent:
                setattr(obj, 'hide_id', {})

        return fn

    @staticmethod
    def mk_setter(cls):
        def fn(obj, **args):
            #obj is the object whose variables are being set
            # args is a dictionary of new variable bindings

            check_dict(args)
            if not hasattr(obj, 'state'):
                obj.state = {}
            tmp = obj.state.copy()
            
            for key, value in args.iteritems():
                # arg variables should be a subset of those in the formal spec
                if key in cls.sorted_state_vars:
                    # and they should pass the type checking
                    cls.state_var_type_checks[key](value)
                    # if so update tmp with the new bindings in args
                    tmp[key] = value
                else:
                    raise TypeError("set: Invalid field name %s" % key)  

            # now check the invariant on tmp
            if not obj.inv(tmp):
                raise TypeError("invariant for class %s violated for init args %s" % (cls.__name__, args))

            # now save the state
            obj.state = tmp

            if 'save_handler' in (cls.custom_handlers):
                cls.custom_handlers['save_handler'](obj, **args)

        return fn

    @staticmethod
    def mk_eq(cls, pred):
        def fn(obj, other):
            return isinstance(other, obj.__class__) and pred(obj, other)
        return fn

    @staticmethod
    def mk_to_client(cls):
        def fn(obj, level=1):
            to_client_var = {}
            for key in cls.sorted_state_vars:
                value = obj.get(key)

                if is_instrumented_list(value) or is_list(value):    
                    to_client_var[key] = []

                    for item in value:
                        if level <= 2:
                            if hasattr(item, 'to_client'):
                                to_client_var[key].append(\
                                    item.to_client(level=level+1))
                            else:
                                to_client_var[key].append(value)
                        else:
                            to_client_var[key].append("Not Printing")
                        
                elif hasattr(value, 'to_client'):
                    to_client_var[key] = value.to_client(level=level+1)
                else:
                    to_client_var[key] = value

            if hasattr(obj, "id"):
                to_client_var["id"] = str(obj.id)

            if hasattr(obj, "hide_id") and 'id' in getattr(obj, "hide_id").keys():
                to_client_var["id"] = str(getattr(obj, "hide_id")["id"])

            return to_client_var

        return fn

    @staticmethod
    def mk_add_attributes(cls):
        def fn(**formals):
            
            check_dict(formals)

            # append the keys of the formals
            cls.sorted_state_vars += formals.keys()

            # create a dictionary of type preds  for the  state variables
            # {'min': is_int, 'max': is_int}
            cls.state_var_type_preds.update(formals.copy())

            # {'min': check_int, 'max': check_int}
            cls.state_var_type_checks = \
            {k: check_pred(v) for k, v in cls.state_var_type_preds.items()}

        return staticmethod(fn)

    @staticmethod
    def mk_getter(cls):
        def fn(obj,k):
            if str(k) and (k in cls.sorted_state_vars):
                if hasattr(obj, 'id') and getattr(obj, 'id') is not None:
                    return getattr(obj, k)
                else:
                    return obj.state[k]
            else:
                raise TypeError("get: Invalid key %s" % k)
    
        return fn
    

    @staticmethod
    def mk_class(_name, **formals):
        # name is the name of the class to be created
        # formals is a dictionary of name, type_pred pairs
        # example of formals: 
        # {'min': is_int, 
        #  'max': is_int, 
        #  'inv': lambda self, args: args['min'] <= args['max']}
        
        # check if formals is a dictionary
        if formals:
            check_dict(formals)

        # create a class with name
        cls = meta(_name)

        # set the invariant
        # if absent in formals, use default (inv_true)
        if 'inv' in formals:
            cls.inv = formals['inv']
            del formals['inv']
        else:
            cls.inv = ClassTemplate.inv_true

        # create sorted list of state variables
        # ['max', 'min']
        cls.sorted_state_vars = []
        cls.sorted_state_vars = sorted(formals.keys())

        # create a dictionary of type preds  for the  state variables
        # {'min': is_int, 'max': is_int}
        cls.state_var_type_preds = {}
        cls.state_var_type_checks = {}
        cls.state_var_type_preds=formals.copy()

        # {'min': check_int, 'max': check_int}
        cls.state_var_type_checks = \
        {k: check_pred(v) for k, v in cls.state_var_type_preds.items()}

        cls.add_attributes = ClassTemplate.mk_add_attributes(cls)
        # __init__
        cls.__init__ = ClassTemplate.mk_init(cls)

        # eq
        # to be done
#       cls.__eq__ = ClassTemplate.mk_eq(cls)

        # get
        cls.get = ClassTemplate.mk_getter(cls)

        # set
        cls.set = ClassTemplate.mk_setter(cls)

        # to_client
        cls.to_client = ClassTemplate.mk_to_client(cls)

        cls.custom_handlers = {}
        cls.is_persistent = False
        cls.custom_handlers['persistence'] = False
        return cls
