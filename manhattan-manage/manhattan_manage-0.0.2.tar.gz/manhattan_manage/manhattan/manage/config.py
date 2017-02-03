import importlib
import inspect
import os

import inflection
from mongoframes import Frame

__all__ = [
    'ManageConfig',
    'ManageConfigMeta'
    ]


class ManageConfigMeta(type):
    """
    The `ManageConfigMeta` class implements defaults and attributes that rely on
    one or more other attributes.

    Some attributes for a `ManageConfig` class are the result of combining one
    or more of the class' attributes. Such attributes can't be combined when the
    class is defined because an overridden attribute would not change any other
    attribute that is based on it.

    To resolve this issue the `ManageConfigMeta` class is used to define
    attribute that are based on other attributes.
    """

    def __new__(meta, name, bases, dct):

        cls = super(ManageConfigMeta, meta).__new__(meta, name, bases, dct)

        # No set up required for the base ManageConfig class
        if name == 'ManageConfig' and not bases:
            return cls

        assert cls.frame_cls is not None, \
                '`frame_cls` not defined for `{0}` class'.format(name)

        # Add lazy attributes
        meta.add_lazy_defaults(cls, name, bases, dct)
        meta.add_lazy_attributes(cls, name, bases, dct)

        return cls

    @classmethod
    def add_lazy_attributes(meta, cls, name, bases, dct):
        """
        Add attributes that are not set directly and rely on other settable
        attributes.
        """

    @classmethod
    def add_lazy_defaults(meta, cls, name, bases,  dct):
        """
        Add default values that use other attributes to determine the default.
        """
        frame_cls = dct['frame_cls']
        filepath = os.path.relpath(inspect.getfile(cls))
        path = os.path.split(filepath)[0]

        # Name
        cls.name = cls.name or \
                inflection.underscore(frame_cls.__name__).replace('_', ' ')
        cls.name_plural = cls.name_plural or inflection.pluralize(cls.name)

        # Var name
        cls.var_name = cls.var_name or cls.name.replace(' ', '_')
        cls.var_name_plural = cls.var_name_plural or \
                cls.name_plural.replace(' ', '_')

        # Blueprint
        if not cls.blueprint_name:
            cls.blueprint_name = path.replace('blueprints/', '').split('/')[0]

        if cls.endpoint_prefix is None:
            if path.split('/')[-1] == 'manage':
                cls.endpoint_prefix = 'manage__'
            else:
                cls.endpoint_prefix = 'manage__' + cls.var_name_plural + '__'

        # Template path
        if not cls.template_path:
            cls.template_path = path.replace('blueprints/', '')


class ManageConfig(metaclass=ManageConfigMeta):
    """
    `ManageConfig` classes provide configuration options for views that manage
    database documents (via `Frame`s). The `manhattan_manage` package provides a
    set of generic manage views (list, view, add, update, delete, ...) which
    rely on a `ManageConfig` class.
    """

    # The `Frame` class being managed
    frame_cls = None

    # The name of the document type being managed in singular and plural form
    name = None
    name_plural = None

    # The name of the document as it would appear as a variable
    var_name = None
    var_name_plural = None

    # The function used to convert a document to a human friendly title
    titleize = str

    # Pagination rules
    per_page = 20
    orphans = 2

    # Typeahead rules - the `typeahead_match_type` can be either 'startswith' or
    # 'contains'.
    typeahead_field = None
    typeahead_id_attr = None
    typeahead_label_attr = None
    typeahead_match_len = 2
    typeahead_match_type = 'startswith'

    # Blueprint
    blueprint_name = None
    endpoint_prefix = None

    # Forms
    add_form = None
    list_form = None
    update_form = None

    # Projections
    list_projection = None
    typeahead_projection = None
    view_projection = None

    # Templates
    template_path = None

    # Fields searched against in the `search` link with generic views
    list_search_fields = None

    @classmethod
    def get_endpoint(cls, view_name):
        """Return the endpoint for a given view"""
        return '{blueprint_name}.{endpoint_prefix}{view_name}'.format(
            blueprint_name=cls.blueprint_name,
            endpoint_prefix=cls.endpoint_prefix,
            view_name=view_name
            )

    @classmethod
    def get_form_cls(cls, view_name):
        """Attempt to return a form class for the given view name"""

        # Check if the form has been defined against the attribute class
        form_attr = view_name + '_form'
        if hasattr(cls, form_attr) and getattr(cls, form_attr):
            return getattr(cls, form_attr)

        # If no form has been defined then we attempt to import it from the
        # expected location.
        module_str = cls.__module__.rsplit('.', 1)[0]

        # Attempt to import the module in which the form would typically be
        # defined.
        try:
            module = importlib.import_module(module_str + '.views.' + view_name)
        except ImportError:
            return None

        # Attempt to extract the form class from the module
        try:
            form_cls_attr = inflection.camelize(form_attr)
            form_cls = getattr(module, form_cls_attr)
        except AttributeError as e:
            print(e)
            return None

        # Store the form class against the config class to speed up future
        # lookups.
        setattr(cls, form_attr, form_cls)

        return form_cls