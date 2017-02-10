import os
from sys import path
from django.core import serializers
from dingus import patch


def load_fixtures(apps, schema_editor, fixture_name):

    with patch('django.core.serializers.python._get_model', lambda model_identifier: apps.get_model(model_identifier)):
        from django.core.management import call_command
        call_command("loaddata", fixture_name)
