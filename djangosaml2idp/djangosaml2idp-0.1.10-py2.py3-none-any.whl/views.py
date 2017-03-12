# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import copy
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
from djangosaml2.conf import get_config
from saml2 import BINDING_HTTP_POST, pack
from saml2.authn_context import (PASSWORD, AuthnBroker,
                                 authn_context_class_ref)
from saml2.config import IdPConfig
from saml2.ident import NameID
from saml2.metadata import entity_descriptor
from saml2.saml import NAMEID_FORMAT_EMAILADDRESS
from saml2.server import Server
from six import text_type

logger = logging.getLogger(__name__)


@csrf_exempt
def login_begin(request, *args, **kwargs):
    """
    Receives a SAML 2.0 AuthnRequest from a Service Provider and
    stores it in the session prior to enforcing login.
    """
    if request.method == 'POST':
        source = request.POST
    else:
        source = request.GET
    # Store these values now, because Django's login cycle won't preserve them.

    try:
        request.session['SAMLRequest'] = source['SAMLRequest']
    except (KeyError, MultiValueDictKeyError):
        return HttpResponseBadRequest('the SAML request payload is missing')

    request.session['RelayState'] = source.get('RelayState', '')
    return redirect('saml_login_process')


@login_required
def login_process(request):
    """
    Processor-based login continuation.
    Presents a SAML 2.0 Assertion for POSTing back to the Service Provider.
    """

    # Construct server with config from settings dict
    conf = IdPConfig()
    conf.load(copy.deepcopy(settings.SAML_IDP_CONFIG))
    IDP = Server(config=conf)
    # Process request
    req_info = IDP.parse_authn_request(request.session['SAMLRequest'], BINDING_HTTP_POST)
    _authn_req = req_info.message
    # Create AuthnResponse
    resp_args = IDP.response_args(_authn_req)
    sso_service = conf.endpoint("single_sign_on_service", binding=BINDING_HTTP_POST)[0]
    AUTHN_BROKER = AuthnBroker()
    AUTHN_BROKER.add(authn_context_class_ref(PASSWORD), "")
    resp_args["authn"] = AUTHN_BROKER.get_authn_by_accr(PASSWORD)
    authn_resp = IDP.create_authn_response(
        identity={}, userid=request.user.username,
        name_id=NameID(format=NAMEID_FORMAT_EMAILADDRESS, sp_name_qualifier=sso_service, name_qualifier=None, text=request.user.email),
        sign_response=True,
        sign_assertion=True,
        **resp_args)
    # Return as html with self-submitting form.
    _dict = pack.factory(BINDING_HTTP_POST, "%s" % authn_resp, req_info.message.assertion_consumer_service_url, request.session['RelayState'], "SAMLResponse")
    return HttpResponse("".join(_dict['data']))


def config_settings_loader(request=None):
    """Utility function to load the pysaml2 configuration.
    """
    conf = IdPConfig()
    conf.load(copy.deepcopy(settings.SAML_IDP_CONFIG))
    return conf


def metadata(request, config_loader_path='djangosaml2idp.views.config_settings_loader', valid_for=None):
    """Returns an XML with the SAML 2.0 metadata for this Idp as configured in the settings.py file.
    """
    conf = get_config(config_loader_path, request)
    metadata = entity_descriptor(conf)
    return HttpResponse(content=text_type(metadata).encode('utf-8'), content_type="text/xml; charset=utf8")
