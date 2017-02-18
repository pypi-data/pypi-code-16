from __future__ import absolute_import
import difflib
from functools import wraps, partial
import re
from flask import request, url_for, current_app
from flask import abort as original_flask_abort
from flask import make_response as original_flask_make_response
from flask.views import MethodView
from flask.signals import got_request_exception
from werkzeug.datastructures import Headers
from werkzeug.exceptions import HTTPException, MethodNotAllowed, NotFound, NotAcceptable, InternalServerError
from werkzeug.http import HTTP_STATUS_CODES
from werkzeug.wrappers import Response as ResponseBase
from flask_restbolt.utils import http_status_message, unpack, OrderedDict
from flask_restbolt.representations.json import output_json
import sys
from flask.helpers import _endpoint_from_view_func
from types import MethodType
import operator
from collections import Mapping



