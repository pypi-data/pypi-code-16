from flask import Flask
from flask import render_template

from . import main

from flask.views import MethodView


class UserView(MethodView):
    def get(self):
        return render_template('index/index.html', )


main.add_url_rule('/', view_func=UserView.as_view('esadfr'))
