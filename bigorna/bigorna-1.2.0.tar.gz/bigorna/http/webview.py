
from flask import Blueprint, render_template, current_app

from bigorna import __VERSION__

web = Blueprint('webview', __name__,
                template_folder='templates',
                static_folder='static')


@web.route('/')
def index():
    return render_template("index.html",
                           jobs=current_app.bigorna.list_jobs(),
                           conf=current_app.cfg,
                           version=__VERSION__)
