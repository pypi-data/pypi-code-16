class ElementalBase(object):
    """
    Root class of Elemental CMS.
    """
    @classmethod
    def iter_elemental_types(cls):
        subclasses = cls.__subclasses__()
        while subclasses:
            subclass = subclasses.pop()
            yield subclass
            subclasses.extend(subclass.__subclasses__())
