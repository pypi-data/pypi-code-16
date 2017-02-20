from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import namedtuple
from functools import wraps
from io import BytesIO
from tempfile import NamedTemporaryFile
from warnings import warn

import numpy as np
from png import Reader
from requests import get
from six import integer_types, string_types, with_metaclass
import traitlets as tr


_REGISTRY = {}


class MetaDocTraits(tr.MetaHasTraits):

    def __new__(mcs, name, bases, classdict):
        def sphinx(trait_name, trait):
            if isinstance(trait, Steno3DTrait):
                return trait.sphinx(trait_name)
            return (
                ':param {name}: {doc}\n:type {name}: '
                ':class:`{cls} <.{cls}>`'.format(
                    name=trait_name,
                    doc=trait.help,
                    cls=trait.__class__.__name__
                )
            )

        def is_required(trait):
            return not trait.allow_none

        def is_deprecated(trait):
            return isinstance(trait, Renamed)

        def is_optional(trait):
            return not is_required(trait) and not is_deprecated(trait)

        trait_dict = {}
        for base in reversed(bases):
            if issubclass(base, tr.HasTraits):
                trait_dict.update(base.class_traits())

        trait_dict.update({key: value for key, value in classdict.items()
                           if isinstance(value, tr.TraitType)})

        doc_str = classdict.get('__doc__', '')
        req = {key: value for key, value in trait_dict.items()
               if is_required(value)}
        opt = {key: value for key, value in trait_dict.items()
               if is_optional(value)}
        dep = {key: value for key, value in trait_dict.items()
               if is_deprecated(value)}
        if req:
            doc_str += '\n\n**Required**\n\n' + '\n'.join(
                (value.sphinx(key) for key, value in req.items())
            )
        if opt:
            doc_str += '\n\n**Optional**\n\n' + '\n'.join(
                (value.sphinx(key) for key, value in opt.items())
            )
        if dep:
            doc_str += '\n\n**Deprecated**\n\n' + '\n'.join(
                (value.sphinx(key) for key, value in dep.items())
            )
        classdict['__doc__'] = doc_str.strip()

        newcls = super(MetaDocTraits, mcs).__new__(mcs, name, bases, classdict)
        _REGISTRY[name] = newcls
        return newcls


def validator(func):
    """wrapper used on validation functions to recursively validate"""
    @wraps(func)
    def func_wrapper(self):
        if getattr(self, '_validating', False):
            return
        self._cross_validation_lock = False
        self._validating = True
        try:
            trait_dict = self._non_deprecated_traits()
            for k in trait_dict:
                if k in self._trait_values:
                    val = getattr(self, k)
                    trait_dict[k]._validate(self, val)
                    if isinstance(val, DelayedValidator):
                        val.validate()
                    if isinstance(trait_dict[k], Repeated):
                        if len(val) == 0 and not trait_dict[k].allow_none:
                            raise tr.TraitError(
                                'Repeated property must have at least '
                                'one value: {}'.format(k)
                            )
                        for v in val:
                            if isinstance(v, DelayedValidator):
                                v.validate()
                elif not trait_dict[k].allow_none:
                    raise tr.TraitError(
                        'Required property not set: {}'.format(k)
                    )
        finally:
            self._cross_validation_lock = True
            self._validating = False
        return func(self)
    return func_wrapper


class DelayedValidator(tr.HasTraits):

    def __init__(self, *args, **kwargs):
        self._cross_validation_lock = True
        super(DelayedValidator, self).__init__(*args, **kwargs)

    @validator
    def validate(self):
        return True


class HasSteno3DTraits(with_metaclass(MetaDocTraits, DelayedValidator)):

    def __init__(self, **metadata):
        self._dirty_traits = set()
        for key in metadata:
            if key not in self.trait_names():
                raise KeyError('{}: Keyword input is not trait'.format(key))
        super(HasSteno3DTraits, self).__init__(**metadata)

    @tr.observe(tr.All)
    def _mark_dirty(self, change):
        self._dirty_traits.add(change['name'])

    def _mark_clean(self, recurse=True):
        self._dirty_traits = set()
        if not recurse or getattr(self, '_inside_clean', False):
            return
        self._inside_clean = True
        try:
            traits = self._dirty
            for trait in traits:
                value = getattr(self, trait)
                if isinstance(value, HasSteno3DTraits):
                    value._mark_clean()
                if isinstance(value, (list, tuple)):
                    for v in value:
                        if isinstance(v, HasSteno3DTraits):
                            v._mark_clean()
        finally:
            self._inside_clean = False

    @property
    def _dirty(self):
        if getattr(self, '_inside_dirty', False):
            return set()
        dirty_instances = set()
        self._inside_dirty = True
        try:
            traits = self._non_deprecated_traits()
            for trait in traits:
                value = getattr(self, trait)
                if (isinstance(value, HasSteno3DTraits) and
                        len(value._dirty) > 0):
                    dirty_instances.add(trait)
                if isinstance(value, (list, tuple)):
                    for v in value:
                        if (isinstance(v, HasSteno3DTraits) and
                                len(v._dirty) > 0):
                            dirty_instances.add(trait)
        finally:
            self._inside_dirty = False
        return self._dirty_traits.union(dirty_instances)

    def _non_deprecated_traits(self):
        return {k: v for k, v in self.traits().items()
                if not isinstance(v, Renamed)}



class Steno3DTrait(object):
    """A mixin for identifying and documenting steno3d traits"""

    sphinx_extra = ''

    @property
    def sphinx_class(self):
        return ':class:`{cls} <.{cls}>`'.format(cls=self.__class__.__name__)

    def sphinx(self, name):
        if not isinstance(self, tr.TraitType):
            return ''
        return (
            ':param {name}: {doc}{default}\n:type {name}: {cls}'.format(
                name=name,
                doc=self.help + self.sphinx_extra,
                default=('' if (self.default_value is tr.Undefined or
                                self.default_value is None or
                                self.default_value in ([], {}, ''))
                         else ', Default: ' + str(self.default_value)),
                cls=self.sphinx_class
            )
        )


class Steno3DNumber(Steno3DTrait):

    @property
    def sphinx_extra(self):
        if (getattr(self, 'min', None) is None and
                getattr(self, 'max', None) is None):
            return ''
        return ', Range: [{mn}, {mx}]'.format(
            mn='-inf' if getattr(self, 'min', None) is None else self.min,
            mx='inf' if getattr(self, 'max', None) is None else self.max
        )


class Int(Steno3DNumber, tr.Int):
    pass


class Float(Steno3DNumber, tr.Float):
    pass


class Bool(Steno3DTrait, tr.Bool):
    pass


class Union(Steno3DTrait, tr.Union):

    @property
    def sphinx_class(self):
        for t in self.trait_types:
            if not isinstance(t, Steno3DTrait):
                return super(Union, self).sphinx_class
        return ', '.join(t.sphinx_class for t in self.trait_types)

    def info(self):
        return " or ".join([tt.info() for tt in self.trait_types])


class Color(Steno3DTrait, tr.TraitType):
    """A trait for rgb, hex, or string colors. Converts to rgb."""

    default_value = 'RANDOM'
    info_text = ('a color (RGB with values 0-255, hex color e.g. \'#FF0000\', '
                 'string color name, or \'random\')')
    sphinx_extra = ', Format: RGB, hex, or predefined color'

    def validate(self, obj, value):
        """check if input is valid color and converts to RBG"""
        if isinstance(value, string_types):
            if value in COLORS_NAMED:
                value = COLORS_NAMED[value]
            if value.upper() == 'RANDOM':
                value = COLORS_20[np.random.randint(0, 20)]
            value = value.upper().lstrip('#')
            if len(value) == 3:
                value = ''.join(v*2 for v in value)
            if len(value) != 6:
                self.error(obj, value)
            try:
                value = [
                    int(value[i:i + 6 // 3], 16) for i in range(0, 6, 6 // 3)
                ]
            except ValueError:
                self.error(obj, value)
        if not isinstance(value, (list, tuple)):
            self.error(obj, value)
        if len(value) != 3:
            self.error(obj, value)
        for v in value:
            if not isinstance(v, integer_types) or not 0 <= v <= 255:
                self.error(obj, value)
        return tuple(value)


class String(Steno3DTrait, tr.TraitType):
    """A trait for strings, where you can map several values to one"""

    def __init__(self, choices=None, lowercase=False, strip=' ',
                 default_value=tr.Undefined, **metadata):
        if choices is None:
            choices = {}
        if not isinstance(choices, (list, tuple, dict)):
            raise tr.TraitError('choices must be a list, tuple, or dict')
        if isinstance(choices, (list, tuple)):
            choices = {v: v for v in choices}
        for k, v in choices.items():
            if not isinstance(v, (list, tuple)):
                choices[k] = [v]
        for k, v in choices.items():
            if not isinstance(k, string_types):
                raise tr.TraitError('choices must be strings')
            for val in v:
                if not isinstance(val, string_types):
                    raise tr.TraitError('choices must be strings')
        self.lowercase = lowercase
        self.strip = strip
        self.choices = choices
        if metadata.get('allow_none', False) and default_value is tr.Undefined:
            default_value = None
        super(String, self).__init__(default_value=default_value, **metadata)

    def validate(self, obj, value):
        """check that input is string and in choices, if applicable"""
        if not isinstance(value, string_types):
            self.error(obj, value)
        if self.strip is not None:
            value = value.strip(self.strip)
        if self.choices is not None and len(self.choices) != 0:
            for k, v in self.choices.items():
                if (value.upper() == k.upper() or
                        value.upper() in [_.upper() for _ in v]):
                    return k.lower() if self.lowercase else k
            self.error(obj, value)
        return value.lower() if self.lowercase else value

    def info(self):
        """description of string trait"""
        if self.choices is not None and len(self.choices) != 0:
            result = 'any of ' + ', '.join(self.choices)
        else:
            result = 'a string'
        if self.allow_none:
            return result + ' or None'
        return result

    @property
    def sphinx_extra(self):
        if self.choices is None or len(self.choices) == 0:
            return ''
        return ', Choices: ' + ', '.join(self.choices)


class Image(Steno3DTrait, tr.TraitType):
    """A trait for PNG images"""

    info_text = 'a PNG image file'
    sphinx_extra = ', Format: PNG'

    def validate(self, obj, value):
        """checks that image file is PNG and gets a copy"""
        if getattr(value, '__valid__', False):
            return value

        try:
            if hasattr(value, 'read'):
                Reader(value).validate_signature()
            else:
                with open(value, 'rb') as v:
                    Reader(v).validate_signature()
        except Exception:
            self.error(obj, value)

        output = BytesIO()
        output.name = 'texture.png'
        output.__valid__ = True
        if hasattr(value, 'read'):
            fp = value
            fp.seek(0)
        else:
            fp = open(value, 'rb')
        output.write(fp.read())
        output.seek(0)
        fp.close()
        return output

    @classmethod
    def download(cls, url):
        im_resp = get(url)
        if im_resp.status_code != 200:
            raise IOError('Failed to download image.')
        output = BytesIO()
        output.name = 'texture.png'
        for chunk in im_resp:
            output.write(chunk)
        output.seek(0)
        return output


FileProp = namedtuple('FileProp', ['file', 'dtype'])


class Array(Steno3DTrait, tr.TraitType):
    """A trait for serializable float or int arrays"""

    def __init__(self, shape=('*',), dtype=(float, int), **metadata):
        if not isinstance(shape, tuple):
            raise tr.TraitError("{}: Invalid shape - must be a tuple "
                                "(e.g. ('*',3) for an array of length-3 "
                                "arrays)".format(shape))
        for s in shape:
            if s != '*' and not isinstance(s, integer_types):
                raise tr.TraitError("{}: Invalid shape - values "
                                    "must be '*' or int".format(shape))
        self.shape = shape

        if not isinstance(dtype, (list, tuple)):
            dtype = (dtype,)
        if (float not in dtype and
                len(set(dtype).intersection(integer_types)) == 0):
            raise tr.TraitError("{}: Invalid dtype - must be int "
                                "and/or float".format(dtype))
        self.dtype = dtype
        super(Array, self).__init__(**metadata)

    def info(self):
        return 'a list or numpy array of {type} with shape {shp}'.format(
            type=', '.join([str(t) for t in self.dtype]),
            shp=self.shape
        )

    @property
    def sphinx_extra(self):
        return ', Shape: {shp}, Type: {dtype}'.format(
            shp='(' + ', '.join(['\*' if s == '*' else str(s)
                                 for s in self.shape]) + ')',
            dtype=self.dtype
        )

    def validate(self, obj, value):
        """Determine if array is valid based on shape and dtype"""
        if not isinstance(value, (list, np.ndarray)):
            self.error(obj, value)
        value = np.array(value)
        if (value.dtype.kind == 'i' and
                len(set(self.dtype).intersection(integer_types)) == 0):
            self.error(obj, value)
        if value.dtype.kind == 'f' and float not in self.dtype:
            self.error(obj, value)
        if len(self.shape) != value.ndim:
            self.error(obj, value)
        for i, s in enumerate(self.shape):
            if s != '*' and value.shape[i] != s:
                self.error(obj, value)
        return value

    def serialize(self, data):
        """Convert the array data to a serialized binary format"""
        if isinstance(data.flatten()[0], np.floating):
            use_dtype = '<f4'
            nan_mask = ~np.isnan(data)
            assert np.allclose(
                    data.astype(use_dtype)[nan_mask], data[nan_mask]), \
                'Converting the type should not screw things up.'
        elif isinstance(data.flatten()[0], np.integer):
            use_dtype = '<i4'
            assert (data.astype(use_dtype) == data).all(), \
                'Converting the type should not screw things up.'
        else:
            raise Exception('Must be a float or an int: {}'.format(data.dtype))

        data_file = NamedTemporaryFile('rb+', suffix='.dat')
        data.astype(use_dtype).tofile(data_file.file)
        data_file.seek(0)
        return FileProp(data_file, use_dtype)

    @classmethod
    def download(cls, url, shape, dtype=float):
        arr_resp = get(url)
        if arr_resp.status_code != 200:
            raise IOError('Failed to download array.')
        data_file = NamedTemporaryFile()
        for chunk in arr_resp:
            data_file.write(chunk)
        data_file.seek(0)
        arr = np.fromfile(data_file.file, dtype).reshape(shape)
        data_file.close()
        return arr


class Vector(Array):
    """A trait for 3D vectors

    Must be a length-3 array. Int vectors are casted to Float vectors.
    X, Y, and Z are also valid inputs. These correspond to [1., 0, 0],
    [0, 1., 0], and [0, 0, 1.] respectively
    """

    def __init__(self, **metadata):
        super(Vector, self).__init__(
            shape=(3,), dtype=(float, int), **metadata
        )

    def validate(self, obj, value):
        if isinstance(value, string_types):
            if value.upper() == 'X':
                value = [1., 0, 0]
            elif value.upper() == 'Y':
                value = [0., 1, 0]
            elif value.upper() == 'Z':
                value = [0., 0, 1]
        if not isinstance(value, (list, np.ndarray)):
            self.error(obj, value)
        value = np.array(value)
        if value.dtype.kind not in ('f', 'i'):
            self.error(obj, value)
        value = value.astype('float')
        if value.ndim == 2 and value.shape[0] == 1:
            value = value[0]
        if value.ndim != 1:
            self.error(obj, value)
        if len(value) != 3:
            self.error(obj, value)
        return value

    @staticmethod
    def as_length(vector, new_length):
        length = np.sqrt(np.sum(vector**2))
        if length == 0:
            raise ZeroDivisionError('Cannot resize vector of length 0')
        return new_length*vector/length

    @staticmethod
    def normalize(vector):
        return Vector.as_length(vector, 1)


class KeywordInstance(Steno3DTrait, tr.Instance):
    """An instance trait that can be constructed with only a keyword dict"""

    def __init__(self, klass=None, args=(), kw=None, **metadata):
        if klass is None:
            raise tr.TraitError('KeywordInstance klass cannot be None')
        super(KeywordInstance, self).__init__(klass, args, kw, **metadata)

    def _resolve_string(self, string):
        try:
            return _REGISTRY[string]
        except KeyError:
            return super(KeywordInstance, self)._resolve_string(string)

    def validate(self, obj, value):
        if isinstance(value, self.klass):
            return value
        if isinstance(value, dict):
            try:
                return self.klass(**value)
            except:
                self.error(obj, value)
        try:
            return self.klass(value)
        except:
            self.error(obj, value)

    def info(self):
        if isinstance(self.klass, string_types):
            klass = self.klass
        else:
            klass = self.klass.__name__
        result = tr.class_of(klass)
        result = result + ' or a keyword dictionary to construct ' + result
        if self.allow_none:
            return result + ' or None'
        return result

    @property
    def sphinx_class(self):
        if isinstance(self.klass, string_types):
            kls = self.klass
        else:
            kls = self.klass.__name__
        return ':class:`{cls} <.{cls}>`'.format(cls=kls)


class Repeated(Steno3DTrait, tr.List):
    """A list trait that creates a length-1 list if given an instance"""

    @property
    def sphinx_class(self):
        if self._trait is None or not isinstance(self._trait, Steno3DTrait):
            return super(Repeated, self).sphinx_class
        return self._trait.sphinx_class

    @property
    def sphinx_extra(self):
        message = ' (Multiple values may be specified using a list)'
        if self._trait is not None and isinstance(self._trait, Steno3DTrait):
            return self._trait.sphinx_extra + message
        return message

    def get(self, obj, cls=None):
        value = super(Repeated, self).get(obj, cls)
        return [v for v in value]

    def validate(self, obj, value):
        if not isinstance(value, (list, tuple)):
            value = [value]
        return super(Repeated, self).validate(obj, value)


class Renamed(Steno3DTrait, tr.TraitType):
    """For renamed traits, warns and reassigns"""

    def __init__(self, new_name, **metadata):
        self.new_name = new_name
        super(Renamed, self).__init__(allow_none=True, **metadata)

    @property
    def sphinx_class(self):
        return ''

    @property
    def sphinx_extra(self):
        return ('This trait is deprecated and may be removed in the future. '
                'Please use **{}** instead.'.format(self.new_name))

    def _warn(self):
        warn(
            '\n`{}` trait deprecated and may be removed in the future. '
            'Please use `{}`.'.format(self.name, self.new_name),
            FutureWarning, stacklevel=3
        )

    def get(self, obj, cls=None):
        self._warn()
        return getattr(obj, self.new_name)

    def set(self, obj, value):
        self._warn()
        return setattr(obj, self.new_name, value)


COLORS_20 = [
    '#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c',
    '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5',
    '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f',
    '#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5'
]

COLORS_NAMED = dict(
    aliceblue="F0F8FF", antiquewhite="FAEBD7", aqua="00FFFF",
    aquamarine="7FFFD4", azure="F0FFFF", beige="F5F5DC",
    bisque="FFE4C4", black="000000", blanchedalmond="FFEBCD",
    blue="0000FF", blueviolet="8A2BE2", brown="A52A2A",
    burlywood="DEB887", cadetblue="5F9EA0", chartreuse="7FFF00",
    chocolate="D2691E", coral="FF7F50", cornflowerblue="6495ED",
    cornsilk="FFF8DC", crimson="DC143C", cyan="00FFFF",
    darkblue="00008B", darkcyan="008B8B", darkgoldenrod="B8860B",
    darkgray="A9A9A9", darkgrey="A9A9A9", darkgreen="006400",
    darkkhaki="BDB76B", darkmagenta="8B008B", darkolivegreen="556B2F",
    darkorange="FF8C00", darkorchid="9932CC", darkred="8B0000",
    darksalmon="E9967A", darkseagreen="8FBC8F", darkslateblue="483D8B",
    darkslategray="2F4F4F", darkslategrey="2F4F4F", darkturquoise="00CED1",
    darkviolet="9400D3", deeppink="FF1493", deepskyblue="00BFFF",
    dimgray="696969", dimgrey="696969", dodgerblue="1E90FF",
    irebrick="B22222", floralwhite="FFFAF0", forestgreen="228B22",
    fuchsia="FF00FF", gainsboro="DCDCDC", ghostwhite="F8F8FF",
    gold="FFD700", goldenrod="DAA520", gray="808080",
    grey="808080", green="008000", greenyellow="ADFF2F",
    honeydew="F0FFF0", hotpink="FF69B4", indianred="CD5C5C",
    indigo="4B0082", ivory="FFFFF0", khaki="F0E68C",
    lavender="E6E6FA", lavenderblush="FFF0F5", lawngreen="7CFC00",
    lemonchiffon="FFFACD", lightblue="ADD8E6", lightcoral="F08080",
    lightcyan="E0FFFF", lightgoldenrodyellow="FAFAD2", lightgray="D3D3D3",
    lightgrey="D3D3D3", lightgreen="90EE90", lightpink="FFB6C1",
    lightsalmon="FFA07A", lightseagreen="20B2AA", lightskyblue="87CEFA",
    lightslategray="778899", lightslategrey="778899", lightsteelblue="B0C4DE",
    lightyellow="FFFFE0", lime="00FF00", limegreen="32CD32",
    linen="FAF0E6", magenta="FF00FF", maroon="800000",
    mediumaquamarine="66CDAA", mediumblue="0000CD", mediumorchid="BA55D3",
    mediumpurple="9370DB", mediumseagreen="3CB371", mediumslateblue="7B68EE",
    mediumspringgreen="00FA9A", mediumturquoise="48D1CC",
    mediumvioletred="C71585", midnightblue="191970", mintcream="F5FFFA",
    mistyrose="FFE4E1", moccasin="FFE4B5", navajowhite="FFDEAD",
    navy="000080", oldlace="FDF5E6", olive="808000",
    olivedrab="6B8E23", orange="FFA500", orangered="FF4500",
    orchid="DA70D6", palegoldenrod="EEE8AA", palegreen="98FB98",
    paleturquoise="AFEEEE", palevioletred="DB7093", papayawhip="FFEFD5",
    peachpuff="FFDAB9", peru="CD853F", pink="FFC0CB",
    plum="DDA0DD", powderblue="B0E0E6", purple="800080",
    rebeccapurple="663399", red="FF0000", rosybrown="BC8F8F",
    royalblue="4169E1", saddlebrown="8B4513", salmon="FA8072",
    sandybrown="F4A460", seagreen="2E8B57", seashell="FFF5EE",
    sienna="A0522D", silver="C0C0C0", skyblue="87CEEB",
    slateblue="6A5ACD", slategray="708090", slategrey="708090",
    snow="FFFAFA", springgreen="00FF7F", steelblue="4682B4",
    tan="D2B48C", teal="008080", thistle="D8BFD8",
    tomato="FF6347", turquoise="40E0D0", violet="EE82EE",
    wheat="F5DEB3", white="FFFFFF", whitesmoke="F5F5F5",
    yellow="FFFF00", yellowgreen="9ACD32"
)
