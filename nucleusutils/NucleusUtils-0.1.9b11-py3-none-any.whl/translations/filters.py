from jinja2 import Undefined

from NucleusUtils.translations.text_utils import get_num_ending

NUMBER = '%N'


def number_ending(number=0, one=None, four=None, five=None, zero=None):
    if number is None or isinstance(number, Undefined):
        number = 0
    if number == 0 and zero:
        return zero.replace(NUMBER, str(number))
    return get_num_ending(number, (one, four, five)).replace(NUMBER, str(number))

