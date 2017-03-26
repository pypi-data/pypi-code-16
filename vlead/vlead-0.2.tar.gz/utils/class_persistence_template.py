
# -*- coding: utf-8 -*-
from type_utils import *
from custom_exceptions import *
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class ClassPersistenceTemplate():
    @staticmethod
    def mk_persistent(cls, uk_list, **table_args):
        check_list(uk_list)
        setattr(cls, 'unique_key_list', uk_list)
    
        check_dict(table_args)
        for key, value in table_args.iteritems():
            setattr(cls, key, value)
        '''http://stackoverflow.com/questions/9539052/how-to-dynamically-change-base-class-of-instances-at-runtime
'''
        cls.is_persistent = True
        cls = type(cls.__name__, (db.Model,), dict(cls.__dict__))

        cls.save = ClassPersistenceTemplate.mk_save(cls)
        cls.delete = ClassPersistenceTemplate.mk_delete(cls)
        cls.get_by_id = ClassPersistenceTemplate.mk_get_by_id(cls)
        cls.get_all = ClassPersistenceTemplate.mk_get_all(cls)
        cls.apply_filters = ClassPersistenceTemplate.mk_apply_filters(cls)
        cls.set_hidden_id = ClassPersistenceTemplate.mk_set_hidden_id(cls)
        ClassPersistenceTemplate.mk_save_handler(cls)
        return cls

    @staticmethod
    def mk_save(cls) :
        def fn(obj, update=False, **args):

            def db_object_and_not_retrieved_from_db(val):
                return hasattr(val, 'id') and getattr(val, 'id') is None

            def retrieve_from_db(value):
                for unique_key in value.__class__.unique_key_list:
                    args_dict = {}
                    args_dict[unique_key] = value.get(unique_key)
                
                new_val = value.__class__.apply_filters(**args_dict)[0]
                return new_val
            
            def setup_the_object(attributes_to_set):
                for key, value in attributes_to_set.iteritems():
                    new_val = None
                    if is_list(value):
                        new_val_list = []
                        for item in value:
                            if db_object_and_not_retrieved_from_db(item):
                                new_val_list.append(retrieve_from_db(item))
                            else:
                                new_val_list.append(item)
                            
                        new_val = new_val_list
                    else:
                        if db_object_and_not_retrieved_from_db(value):
                            new_val = retrieve_from_db(value)
                        else:
                            new_val = value
                                
                    setattr(obj, key, new_val)

            if (update):
                attributes_to_set = args
            else:
                attributes_to_set = obj.state
            
            setup_the_object(attributes_to_set)
            
            db.session.autoflush = False
            db.session.add(obj)
            db.session.commit()

        return fn

    @staticmethod
    def mk_save_handler(cls):
        def fn(obj, **args):
            obj.save(update=True, **args)

        cls.custom_handlers['save_handler'] = fn

    @staticmethod
    def mk_delete(cls):
        def fn(obj):
            db.session.autoflush = False
            db.session.delete(obj)
            db.session.commit()

        return fn

    @staticmethod
    def mk_set_state(cls):
        def fn(obj):
            obj.state = {}

        return staticmethod(fn)

    @staticmethod
    def mk_get_by_id(cls):
        def fn(id):
            db.session.autoflush = False
            obj = cls.query.get(id)
            return obj

        return staticmethod(fn)

    @staticmethod
    def mk_get_all(cls):
        def fn():
            db.session.autoflush = False
            lst = cls.query.all()
            return lst

        return staticmethod(fn)

    @staticmethod
    def mk_apply_filters(cls):
        def fn(**kwargs):
            db.session.autoflush = False
            for key, value in kwargs.iteritems():
                if not (is_str(value) or is_unicode(value) or
                            is_none(value) or is_int(value) or
                            is_date(value)):
                   for unique_key in value.__class__.unique_key_list:
                       args_dict = {}
                       args_dict[unique_key] = value.get(unique_key)

                   kwargs[key] = value.__class__.apply_filters(**args_dict)[0]

            lst = cls.query.filter_by(**kwargs).all()

            if not lst:
                raise NotFoundError("The object is not found")
            else:
                return lst

        return staticmethod(fn)

    @staticmethod
    def mk_set_hidden_id(cls):
        def fn(obj, id):
            obj.hide_id["id"] = id

        return staticmethod(fn)
