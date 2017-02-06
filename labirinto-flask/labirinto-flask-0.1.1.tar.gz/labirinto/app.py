# -*- coding: utf-8 -*-

from flask import *
from flask_security import Security, MongoEngineUserDatastore
from flask_bootstrap import Bootstrap

from blueprints.salas import salas_blueprint
from blueprints.sessoes import sessoes_blueprint
from blueprints.index import index_blueprint
from db import db
from modelos import Grupo, Usuario
import admin

from os import path


def create_app(modo='dev'):
    instance_path = path.join(path.abspath(path.dirname(__file__)), 'instancias', modo)
    # App e blueprints
    app = Flask('labirinto', instance_path=instance_path, instance_relative_config=True)
    app.register_blueprint(salas_blueprint)
    app.register_blueprint(sessoes_blueprint)
    app.register_blueprint(index_blueprint)
    # Configurações
    app.config.from_pyfile('config.py')
    # Plugins
    db.init_app(app)
    Security(app=app, datastore=MongoEngineUserDatastore(db, Usuario, Grupo))
    Bootstrap(app)
    admin.configura(app)
    return app
