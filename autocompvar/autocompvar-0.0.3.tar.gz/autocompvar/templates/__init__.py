#!/usr/bin/env python
# -*- coding: utf-8 -*-

from jinja2 import Environment, PackageLoader

env = Environment(
    loader=PackageLoader('autocompvar', 'templates'),
)
t_def_all_class = env.get_template("def_all_class.txt")
t_def_class = env.get_template("def_class.txt")
t_code = env.get_template("code.txt")

if __name__ == "__main__":
    """
    """
    from autocompvar.packages.nameddict import Base as GenericData
    from autocompvar.metadata import ClassDef, ClassInstance
    
#     def test_t_new_instance():
#         cls_inst = ClassInstance(
#             classname="user",
#             attrs=["id", "name"],
#             keys=["id", "name"],
#             data={"id": 1, "name": 2},
#         )
#         
#     test_t_new_instance()