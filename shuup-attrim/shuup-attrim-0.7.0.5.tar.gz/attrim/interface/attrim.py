"""
This modules imports all here only for handy use of `attrs` namespace. So users 
don't need to write something frustrating like:

    from attrim.models import Class
    from attrim.types import Type
    
    
    Class.objects.create(code='code', type=Type.INT)

and they can write instead:

    from attrim.interface import attrim
    
    
    attrim.cls.create(code='code', type=attrim.Type.INT, ...)
    
    attrim.filter_products_by(cls_code='code', option_values=[5, 8])

"""
from attrim.types import AttrimType
from attrim.interface import cls
from attrim.interface.filters import filter_product_qs_by
