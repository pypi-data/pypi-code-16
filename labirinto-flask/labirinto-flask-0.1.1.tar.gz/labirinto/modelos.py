# -*- coding: utf-8 -*-

from flask_security import UserMixin, RoleMixin
from flask_security.utils import encrypt_password

from db import db


class Sessao(db.Document):
    """Sessão de usuário, sem segurança qualquer"""
    nome = db.StringField(unique=True)
    url = db.StringField()


class Grupo(db.Document, RoleMixin):
    """Grupo de permissões usado pelo flask-security"""
    nome = db.StringField(max_length=80, unique=True)
    descricao = db.StringField(max_length=255)

    @classmethod
    def cria_grupo(cls, nome, descricao=None):
        return cls.objects.create(nome=nome, descricao=descricao)


class Usuario(db.Document, UserMixin):
    """Usuário, seguro com senha, participante de grupos e talz"""
    nome = db.StringField(max_length=255)
    email = db.EmailField(max_length=255, unique=True)
    password = db.StringField(max_length=255)
    active = db.BooleanField(default=True)
    roles = db.ListField(db.ReferenceField(Grupo, reverse_delete_rule=db.DENY), default=[])

    @classmethod
    def cria_usuario(cls, nome, password, roles=None, active=True):
        return cls(nome=nome, password=password, roles=roles, active=active)
