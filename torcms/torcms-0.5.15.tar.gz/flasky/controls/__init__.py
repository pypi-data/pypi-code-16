from flask import Blueprint
main = Blueprint('handler', __name__)
from . import post
from . import index