# flake8: noqa: E221

from byte import Model, Property


class ItemModelBasic(Model):
    id      = Property(int)
    title   = Property(str, max_length=50)

    alpha   = Property(int)
    beta    = Property(int)
    charlie = Property(int)
    delta   = Property(int)
    epsilon = Property(int)


class ItemModelSlots(Model):
    class Options:
        slots = True

    id      = Property(int)
    title   = Property(str, max_length=50)

    alpha   = Property(int)
    beta    = Property(int)
    charlie = Property(int)
    delta   = Property(int)
    epsilon = Property(int)


class ItemBasic(object):
    def __init__(self):
        self.id = None
        self.title = None

        self.alpha = None
        self.beta = None
        self.charlie = None
        self.delta = None
        self.epsilon = None


class ItemSlots(object):
    __slots__ = ('id', 'title', 'alpha', 'beta', 'charlie', 'delta', 'epsilon')

    def __init__(self):
        self.id = None
        self.title = None

        self.alpha = None
        self.beta = None
        self.charlie = None
        self.delta = None
        self.epsilon = None


if __name__ == '__main__':
    import sys

    def get_size(obj, seen=None):
        size = sys.getsizeof(obj)

        if seen is None:
            seen = set()

        obj_id = id(obj)

        if obj_id in seen:
            return 0

        # Important mark as seen *before* entering recursion to gracefully handle
        # self-referential objects
        seen.add(obj_id)

        if isinstance(obj, dict):
            size += sum([get_size(v, seen) for v in obj.values()])
            size += sum([get_size(k, seen) for k in obj.keys()])
        elif hasattr(obj, '__dict__'):
            size += get_size(obj.__dict__, seen)
        elif hasattr(obj, '__slots__'):
            for key in obj.__slots__:
                size += get_size(getattr(obj, key))
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
            size += sum([get_size(i, seen) for i in obj])

        return size

    i_model_basic = ItemModelBasic()
    i_model_basic.id = 1
    i_model_basic.title = 'Cables'
    i_model_basic.alpha = 'alpha'
    i_model_basic.beta = 'beta'
    i_model_basic.charlie = 'charlie'
    i_model_basic.delta = 'delta'
    i_model_basic.epsilon = 'epsilon'

    i_model_slots = ItemModelSlots()
    i_model_slots.id = 1
    i_model_slots.title = 'Cables'
    i_model_slots.alpha = 'alpha'
    i_model_slots.beta = 'beta'
    i_model_slots.charlie = 'charlie'
    i_model_slots.delta = 'delta'
    i_model_slots.epsilon = 'epsilon'

    i_basic = ItemBasic()
    i_basic.id = 1
    i_basic.title = 'Cables'
    i_basic.alpha = 'alpha'
    i_basic.beta = 'beta'
    i_basic.charlie = 'charlie'
    i_basic.delta = 'delta'
    i_basic.epsilon = 'epsilon'

    i_slots = ItemSlots()
    i_slots.id = 1
    i_slots.title = 'Cables'
    i_slots.alpha = 'alpha'
    i_slots.beta = 'beta'
    i_slots.charlie = 'charlie'
    i_slots.delta = 'delta'
    i_slots.epsilon = 'epsilon'

    print('== i_model_basic: %r' % (get_size(i_model_basic),))
    print('== i_model_slots: %r' % (get_size(i_model_slots),))
    print('== i_basic: %r' % (get_size(i_basic),))
    print('== i_slots: %r' % (get_size(i_slots),))
