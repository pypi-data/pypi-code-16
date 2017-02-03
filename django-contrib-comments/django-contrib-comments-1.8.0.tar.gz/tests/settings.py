DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3'}},
INSTALLED_APPS=[
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.admin",
    "django_comments",
    "testapp",
    "custom_comments",
],
MIDDLEWARE=(
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
),
MIDDLEWARE_CLASSES=MIDDLEWARE  # Django < 1.10
ROOT_URLCONF='testapp.urls',
TEMPLATES=[
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.messages.context_processors.messages',
               'django.contrib.messages.context_processors.messages',
            ]
        },
    },
],
SECRET_KEY="it's a secret to everyone",
SITE_ID=1,

