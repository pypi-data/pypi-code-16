from django.conf import settings


def get_languages_list() -> list:
    lang_keys = []
    for lang in settings.LANGUAGES:
        lang_keys.append(lang[0])
    return lang_keys


def get_default_lang_code() -> str:
    return settings.PARLER_DEFAULT_LANGUAGE_CODE
