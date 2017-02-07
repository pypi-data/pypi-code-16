from attrim.helpers import get_languages_list


def require_enabled_languages(*required_languages):
    """
    Throw an error if site setting doesn't contain required languages.
    """
    def real_decorator(function):
        site_languages = get_languages_list()
        for required_lang in required_languages:
            if required_lang not in site_languages:
                raise AttributeError(
                    'Site does not have language required for this test.'
                )
        return function
    return real_decorator
