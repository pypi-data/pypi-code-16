SECRET_KEY = 'fake-key'

INSTALLED_APPS = [
    'ml_markdown.apps.MlMarkdownConfig',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
    },
]
