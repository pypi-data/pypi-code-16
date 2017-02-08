#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from . import templates
    from .name_convention import (
        is_valid_class_name, is_valid_variable_name, is_valid_surfix,
        to_variable_name
    )
    from .exc import ValidationError
    from .packages.six import integer_types, string_types
    from .packages.nameddict import Base as GenericData
except:
    from autocompvar import templates
    from autocompvar.name_convention import (
        is_valid_class_name, is_valid_variable_name, is_valid_surfix, 
        to_variable_name,
    )
    from autocompvar.exc import ValidationError
    from autocompvar.packages.six import integer_types, string_types
    from autocompvar.packages.nameddict import Base as GenericData

from collections import OrderedDict


def validate(metadata, class_def_dict=None):
    """validate metadata, collect class_def_dict we need to implement. 
    """
    if class_def_dict is None:
        class_def_dict = OrderedDict()

    # if it is list:
    if isinstance(metadata, list):
        for md in metadata:
            validate(metadata, class_def_dict)
    elif not isinstance(metadata, dict):
        raise ValidationError("metadata is not a dict")

    # get values
    classname = metadata.get("classname")
    attrs = metadata.get("attrs")
    keys = metadata.get("keys")
    if keys is None:
        keys = attrs
    data = metadata.get("data")
    collection = metadata.get("collection", list())

    # check classname
    if isinstance(classname, string_types):
        if is_valid_class_name(classname):
            class_def = ClassDef(classname, attrs, keys)
            if classname not in class_def_dict:
                class_def_dict[classname] = class_def
            else:
                if not class_def_dict[classname] == class_def:
                    raise ValidationError(
                        "definition of %r is incls_instistent: %s" % (
                            classname, class_def)
                    )
        else:
            raise ValidationError("%r is not a valid class name" % classname)
    else:
        raise ValidationError("classname has to be a string")

    # check attrs
    if not isinstance(attrs, list):
        raise ValidationError("attrs has to be a list")
    for attr in attrs:
        if not isinstance(attr, string_types):
            raise ValidationError("attribute has to be string")
        if not is_valid_variable_name(attr):
            raise ValidationError("%r is a invalid attribute name" % attr)

    # check keys
    if not isinstance(keys, list):
        raise ValidationError("keys has to be a list")
    for key in attrs:
        if key not in attrs:
            raise ValidationError("keys has to be subset of attrs")

    # check data
    if isinstance(data, dict):
        for key in data:
            if key not in attrs:
                raise ValidationError("%r is not defined in attrs" % key)

        for key in keys:
            value = data.get(key)
            if isinstance(value, string_types):
                new_value = value.replace(" ", "_").lower()
                if not is_valid_surfix(new_value):
                    raise ValidationError("%r can't be a valid key" % value)
            elif not isinstance(value, integer_types):
                raise ValidationError("%r can't be a valid key" % value)
    elif data is not None:
        raise ValidationError("data has to be None or a dict")

    # check collection
    if isinstance(collection, list):
        for sub_metadata in collection:
            validate(sub_metadata, class_def_dict)
    elif collection is not None:
        raise ValidationError("collection has to be None or a list")

    return class_def_dict


class ClassDef(object):

    """

    **中文文档**

    用于生成定义类的代码。形如::

        class MyClass(Base):
            __attrs__ = ['id', 'name']
            __keys__ = ['id']

            def __init__(self, id=None, name=None):
                self.id = id
                self.name = name

    :param classname: MyClass
    :param attrs: ['id', 'name'] 部分
    :param keys: ['id'] 部分
    :attr kwargs_text: ', id=None, name=None' 部分
    """

    def __init__(self, classname, attrs, keys=None, **kwargs):
        self.classname = classname
        self.attrs = attrs
        self.keys = keys
        self.kwargs_text = "".join([", %s=None" % attr for attr in attrs])

    def __repr__(self):
        return "%s(%s)" % (
            self.__class__.__name__,
            ", ".join([
                "%s=%r" % (attr, value) for attr, value in self.__dict__.items()
            ])
        )

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @property
    def code(self):
        return templates.t_def_class.render(class_def=self)


class ClassInstance(object):

    def __init__(self, classname, attrs, keys=None, data=None, collection=None):
        self.classname = classname
        self.attrs = attrs
        if keys is None:
            keys = attrs
        self.keys = keys

        self.data = data
        if collection is None:
            self.collection = collection
        else:
            self.collection = [
                self.__class__.load(metadata) for metadata in collection]

    @property
    def instname(self):
        """

        ::

            # User()
            user
        """
        return to_variable_name(self.classname)

    @property
    def varname(self):
        """

        ::

            # User(id=1, name='John')
            user_id_1
        """
        if self.keys:
            return "%s_%s_%s" % (
                to_variable_name(self.classname),
                self.keys[0],
                str(self.data[self.keys[0]]).replace(" ", "_"),
            )
        else:
            return to_variable_name(self.classname)

    @property
    def new_instance_kwargs_text(self):
        """Generate code like: ``id=1, name='John'`` 
        """
        if self.data is None:
            return ""
        else:
            return ", ".join([
                "%s=%r" % (attr, value) for attr, value in self.data.items()
            ])

    @property
    def code_new_instance(self):
        """Generate code like: ``user_id_1 = User(id=1, name='John')``
        """
        return "\n%s = %s(%s)" % (
            self.varname,
            self.classname,
            self.new_instance_kwargs_text,
        )

    @classmethod
    def load(cls, metadata):
        return cls(
            classname=metadata.get("classname"),
            attrs=metadata.get("attrs"),
            keys=metadata.get("keys"),
            data=metadata.get("data"),
            collection=metadata.get("collection"),
        )

    def dump(self):
        metadata = {
            "classname": self.classname,
            "attrs": self.attrs,
            "keys": self.keys,
            "data": self.data,
        }
        if self.collection is None:
            metadata["collection"] = None
        else:
            metadata["collection"] = [
                cls_insttructor.dump() for cls_insttructor in self.collection]
        return metadata


def gen_code_def_part(metadata):
    class_def_dict = validate(metadata)
    class_def_list = list(class_def_dict.values())
    code = templates.t_def_all_class.render(class_def_list=class_def_list)
    return code


def gen_code_inst_part(metadata, do_validate=True, code_snipet=None):
    """广度优先向下遍历所有的容器类和实例类

    1. 凡是遇到一个类, 都创建一次实例
    2. 凡是遇到一个类, 只要有母类, 该类的实例都作为一个属性绑定到母类的实例下

    最后就不 
    """
    if do_validate:
        class_def_dict = validate(metadata)

    if code_snipet is None:
        code_snipet = list()

    if isinstance(metadata, list):
        for md in metadata:
            gen_code_inst_part(md, do_validate=False, code_snipet=code_snipet)

    else:  # dict
        cls_inst = ClassInstance.load(metadata)
        code_snipet.append(cls_inst.code_new_instance)
        if cls_inst.collection:
            for c_i in cls_inst.collection:
                gen_code_inst_part(
                    c_i.dump(), do_validate=False, code_snipet=code_snipet)

                # 建立与上级的联系
                for key in c_i.keys:
                    code_snipet.append("%s.%s____%s = %s" % (
                        cls_inst.varname, 
                        key, 
                        str(c_i.data[key]).replace(" ", "_"), 
                        c_i.varname
                    ))

    return "\n".join(code_snipet)


def gen_code(metadata):
    return templates.t_code.render(
        def_part=gen_code_def_part(metadata),
        inst_part=gen_code_inst_part(metadata),
    )

if __name__ == "__main__":
    from pprint import pprint

    metadata = {
        "classname": "Food",
        "attrs": [],
        "collection": [
            {
                "classname": "FoodCategory",
                "attrs": ["id", "name"],
                "keys": ["name"],
                "data": {"id": 1, "name": "Fruit"},
                "collection": [
                    {
                        "classname": "Fruit",
                        "attrs": ["id", "name"],
                        "keys": ["id", "name"],
                        "data": {"id": 1, "name": "Apple"},
                    },
                    {
                        "classname": "Fruit",
                        "attrs": ["id", "name"],
                        "keys": ["id", "name"],
                        "data": {"id": 2, "name": "Banana"},
                    },
                ],
            },
            {
                "classname": "FoodCategory",
                "attrs": ["id", "name"],
                "keys": ["name"],
                "data": {"id": 2, "name": "Meat"},
                "collection": [
                    {
                        "classname": "Meat",
                        "attrs": ["id", "name"],
                        "keys": ["id", "name"],
                        "data": {"id": 1, "name": "Pork"},
                    },
                    {
                        "classname": "Meat",
                        "attrs": ["id", "name"],
                        "keys": ["id", "name"],
                        "data": {"id": 2, "name": "Beef"},
                    },
                ],
            },
        ],
    }

    def test_ClassDef():
        class_def = ClassDef(**metadata)
        print(class_def.code)
        
        class_def = ClassDef(**metadata["collection"][0])
        print(class_def.code)
        
        class_def = ClassDef(**metadata["collection"][0]["collection"][0])
        print(class_def.code)
        
#     test_ClassDef()

    def test_ClassInstance():
        class_inst = ClassInstance.load(metadata)
        print(class_inst.code_new_instance)
        
        class_inst = ClassInstance.load(metadata["collection"][0])
        print(class_inst.code_new_instance)
        
        class_inst = ClassInstance.load(metadata["collection"][0]["collection"][0])
        print(class_inst.code_new_instance)
        
#     test_ClassInstance()

    def test_gen_code():
        print(gen_code_def_part(metadata))
        print(gen_code_inst_part(metadata))
        
#     test_gen_code()