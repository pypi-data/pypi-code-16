import tempfile
import unittest

import shutil

import os
from django.utils.crypto import get_random_string

import django_configure
import django_configure.type


class ConfigTestCase(unittest.TestCase):
    def tearDown(self):
        super(ConfigTestCase, self).tearDown()

    def setUp(self):
        super(ConfigTestCase, self).setUp()
        self.tmp_dir = os.path.join(tempfile.gettempdir(), 'django-config-test')
        self.config_path = os.path.join(self.tmp_dir, 'testapp.cfg')
        try:
            shutil.rmtree(os.path.dirname(self.config_path))
        except OSError:
            pass

    def test_config_define(self):

        def generate_string():
            chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
            return get_random_string(50, chars)

        generated_secret_string = generate_string()

        config = django_configure.define(description_dict={
            'Common': {
                'secret': django_configure.type.String(default=generated_secret_string),
                'static_root': django_configure.type.String()
            }
        }, default_path=self.config_path)

        self.assertEqual(config.get('Common.secret'), generated_secret_string)
        self.assertEqual(config.get('Common.static_root'), None)

        config_output = config.generate(True)

        self.assertTrue(os.path.exists(self.config_path))
        with open(self.config_path, 'r') as f:
            self.assertMultiLineEqual(config_output, f.read())

    def test_default(self):
        config = django_configure.default(app_name='testapp')
        self.assertTrue(config.get('Common.secret'))

    def test_secret_generation(self):
        config_01 = django_configure.default(app_name='testapp')
        config_02 = django_configure.default(app_name='testapp')

        self.assertNotEqual(config_01.get('Common.secret'), config_02.get('Common.secret'))

    def test_not_overwrite(self):
        config_01 = django_configure.default(app_name='testapp', default_path=self.config_path)
        out_1 = config_01.generate(True)

        with open(self.config_path, 'r') as f:
            self.assertMultiLineEqual(out_1, f.read())

        config_02 = django_configure.default(app_name='testapp', default_path=self.config_path)
        out_2 = config_02.generate(True)

        with open(self.config_path+'.template', 'r') as f:
            self.assertMultiLineEqual(out_2, f.read())

    def test_wsgi(self):
        config_01 = django_configure.default(app_name='testapp', env_prefix='TESTAPP', default_path=self.config_path)

        try:
            os.makedirs(self.tmp_dir)
        except IOError:
            pass

        wsgi_path = os.path.join(self.tmp_dir, 'wsgi.py')
        wsgi_out = config_01.generate_wsgi(wsgi_path)

        with open(wsgi_path, 'r') as f:
            self.assertMultiLineEqual(wsgi_out, f.read())

        # run wsgi code to make env variable available
        exec(wsgi_out)

        self.assertEqual(os.environ[config_01.config_var_name], self.config_path)

    def test_db(self):
        config_01 = django_configure.define(description_dict={
            'Database': {
                'url': django_configure.type.Database()
            }
        })
        sqlite_path = self.tmp_dir+'/db.sqlite'
        os.environ['DATABASE_URL'] = 'sqlite:///'+sqlite_path
        db = config_01.get('Database.url')
        self.assertDictContainsSubset({'ENGINE': 'django.db.backends.sqlite3', 'NAME': sqlite_path}, db)

    def test_env(self):
        config = django_configure.default(app_name='testapp', env_prefix='TESTAPP')
        os.environ['TESTAPP_COMMON_SECRET'] = 'new_secret'
        self.assertEqual('new_secret', config.get('Common.secret'))

if __name__ == '__main__':
    unittest.main()
