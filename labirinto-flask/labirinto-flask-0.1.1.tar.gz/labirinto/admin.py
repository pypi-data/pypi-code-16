# -*- coding: utf-8 -*-

from flask import abort, redirect, request, url_for
from flask_security import current_user
from flask_admin.contrib.mongoengine import ModelView
from flask_admin import Admin

from labirinto.modelos import Sessao, Usuario, Grupo


admin = Admin(template_mode='bootstrap3',
              base_template='admin_base.html')


# ModelView custom
class SafeModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        """
        Redireciona o usuário para página de login ou de acesso negado
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)  # negado, caso não pertença ao grupo admin.
            else:
                return redirect(url_for('security.login', next=request.url))


def configura(app):
    admin.init_app(app)
    admin.add_view(SafeModelView(Sessao))
    admin.add_view(SafeModelView(Usuario, category='contas'))
    admin.add_view(SafeModelView(Grupo, category='contas'))
