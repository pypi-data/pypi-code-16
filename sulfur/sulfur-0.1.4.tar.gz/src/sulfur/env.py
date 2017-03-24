def enable_django():
    """
    Enables all django-related functionality.
    """

    # Uses DjangoClient as the default server interface
    from .client import set_server_class, DjangoClient
    set_server_class(DjangoClient)