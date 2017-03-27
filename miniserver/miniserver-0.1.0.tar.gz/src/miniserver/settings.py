import os


class Settings:
    """
    Represent and store global settings.
    """

    # Settings with default values
    lang = 'en'

    def _get_jinja2_templates_dirs(self):
        base_module = os.path.dirname(__file__)
        miniserver_templates = os.path.join(base_module, 'django_project', 'jinja2')
        user_templates = os.path.join(os.getcwd(), 'templates')
        return [user_templates, miniserver_templates]

    def _get_index_view(self):
        """
        Return the default view your site. This can be overridden by the a
        index route in the main module.
        """

        from .routes import ROUTES

        if '' in ROUTES:
            return ROUTES['']

        from django.shortcuts import render

        def default_index_view(request):
            return render(request, 'index.html', {'settings': settings})

        return default_index_view

    def __setattr__(self, key, value):
        if key.isupper():
            from miniserver.django_project import settings
            setattr(settings, key, value)

        super().__setattr__(key, value)


settings = Settings()