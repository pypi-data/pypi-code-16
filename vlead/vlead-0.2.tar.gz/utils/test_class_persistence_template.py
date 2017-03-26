# -*- coding: utf-8 -*-
import unittest
from flask_testing import TestCase
from datetime import datetime
from type_utils import *
from class_templates import *
from class_persistence_template import *
from flask import Flask
from flask_cors import CORS

def create_app(config):
    # init our app
    app = Flask(__name__)
    app.secret_key = 'djfjsdkjXXS7979dfdfd'
    # init sqlalchemy db instance
    db.init_app(app)
    db.app = app
    return app

config = {
    'SQLALCHEMY_DATABASE_URI': ''
}

class TestPersistence(TestCase):
    TESTING = True

    def create_app(self):
        app = create_app(config)
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def testCreationOfAPersistentClass(self):
        print "testCreationOfAPersistentClass"
        
        Name = ClassTemplate.mk_class("Name")
        Name.add_attributes(name=is_alphabetic_str)

        args = {"__tablename__": "names",
                "id": db.Column(db.Integer, primary_key=True),
                "name": db.Column(db.String(128), nullable=False)
                }
        PName = ClassPersistenceTemplate.mk_persistent(Name, ['name'], **args)
        self.setUp()
        p_name = PName(name="Jimi Hendrix")
        p_name.save()
        name = PName.get_by_id(1)
        self.assertEqual(name.get("name"), "Jimi Hendrix")
        p_name.set(name="Bo Didley")
        names = PName.get_all()
        self.assertEqual(names[0].get("name"), "Bo Didley")
        self.assertEqual(PName.apply_filters(name="Bo Didley")[0].get("name"),
                             "Bo Didley")
        names[0].delete()
        names = PName.get_all()
        self.assertEqual(names, [])

if __name__ == '__main__':
    unittest.main()
