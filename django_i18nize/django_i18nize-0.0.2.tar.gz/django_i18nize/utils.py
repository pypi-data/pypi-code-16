from django.conf import settings

import json
import os
import re

from django.utils.translation import get_language

def get_translation(key, language=None, values=None):
    _language = language or get_language() or 'en'
    filepath = os.path.join(settings.DJANGO_I18NIZE_CONFIG.get('destination_dir'), u'{}.{}'.format(_language, 'json'))

    with open(filepath) as data_file:
        data = json.load(data_file)
        value = data.get(key) or key

        key_variables = re.findall(r'\{\{[^}]*}}', value)

        if values:
            for variable in key_variables:
                key = variable.replace('{', '').replace('}', '').strip()
                variable_value = values.get(key)

                if variable_value:
                    value = value.replace(variable, variable_value)

        return value