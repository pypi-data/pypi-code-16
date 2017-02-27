# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.RST.
# 
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.RST.HTTP_Status
#
# Purpose
#    Define classes handling RESTful responses for HTTP status codes
#
# Revision Dates
#    16-Jul-2012 (CT) Creation
#    23-Jul-2012 (CT) Add argument `response` to `__call__`
#    30-Jul-2012 (CT) Add `template_name`, `Login_Required`
#     6-Aug-2012 (CT) Let `blackboard`
#     8-Aug-2012 (MG) Use a dict for `blackboard`
#    10-Aug-2012 (CT) Add missing import for `CAL.Date_Time`
#    17-Aug-2012 (MG) Use byte data-type for response headers
#    24-Aug-2012 (CT) Change `Status.__repr__` to convert `_msg` to `str`
#    10-Oct-2012 (CT) Set `request.Error` in `Status.__call__`
#    11-Dec-2012 (CT) Add property `info` to `Status`
#    11-Dec-2012 (CT) Change `_add_response_body` to include `message`
#                     (after doing: s/_msg/message/g)
#     2-Mar-2013 (CT) Use `response.set_header`, not `.headers [] = `
#     6-May-2013 (CT) Set `request.Error` to `unicode (.message)`
#     3-Dec-2013 (CT) Add support for `cache_control`;
#                     set `no_cache` for `See_Other`, `Temporary_Redirect`
#    11-Feb-2014 (CT) Add `response`, `template` to `Templateer.Context`
#     3-May-2014 (CT) Add warning to `Found._spec` (don't use it!)
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from   _CAL                     import CAL
from   _GTW                     import GTW
from   _TFL                     import TFL

import _CAL.Delta
import _CAL.Date_Time

import _GTW._RST

from   _TFL._Meta.Once_Property import Once_Property

from   _TFL.I18N                import _, _T, _Tn
from   _TFL.pyk                 import pyk

import _TFL._Meta.M_Class
import _TFL._Meta.Object

import json

class _Meta_ (TFL.Meta.M_Class) :
    """Meta class for HTTP-Status classes"""

    Table         = {}

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        if cls.status_code is not None :
            if cls.status_code not in cls.Table :
                cls.Table [cls.status_code] = cls
            if "description" not in dct :
                cls.description = cls.__name__.capitalize ().replace ("_", " ")
    # end def __init__

    def __getitem__ (cls, key) :
        return cls.Table [key]
    # end def __getitem__

    def __repr__ (cls) :
        if cls.status_code :
            return "<HTTP status %s: %s>" % (cls.status_code, cls.description)
        return cls.__m_super.__repr__ ()
    # end def __repr__

# end class _Meta_

class Status (TFL.Meta.BaM (Exception, TFL.Meta.Object, metaclass = _Meta_)) :
    """Base class for HTTP status exceptions"""

    ### http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html

    cache_control = None
    description   = None
    status_code   = None

    @Once_Property
    def info (self) :
        return self._kw.get ("info")
    # end def info

    @property
    def message (self) :
        return self._msg
    # end def info

    @Once_Property
    def render_man (self) :
        import _GTW._RST.Mime_Type
        import _GTW._RST._TOP.Base
        return GTW.RST.Mime_Type.Render_Man \
            ((GTW.RST.Mime_Type.JSON, GTW.RST.TOP.HTML))
    # end def render_man

    @property
    def template_name (self) :
        return self.status_code
    # end def template_name

    def __init__ (self, message = None, ** kw) :
        assert self.status_code, self
        self.__dict__.update  (kw)
        self.__super.__init__ (message)
        self._msg = message
        self._kw  = kw
    # end def __init__

    def __call__ (self, resource, request, response) :
        if not hasattr (request, "Error") :
            if self.message :
                ### Backwards compatibility with old-style Jinja templates
                try :
                    request.Error = pyk.text_type (self.message)
                except Exception :
                    request.Error = str (self.message)
        response.status_code  = self.status_code
        self._add_response_body     (resource, request, response)
        self._add_response_headers  (resource, request, response)
        if self.cache_control :
            self._add_cache_control (resource, request, response)
        return response
    # end def __call__

    def _add_cache_control (self, resource, request, response) :
        cc  = self.cache_control
        rcc = response.cache_control
        if cc :
            for k, v in cc.items () :
                setattr (rcc, k, v)
    # end def _add_cache_control

    def _add_response_body (self, resource, request, response) :
        with resource.LET (ignore_picky_accept = True) :
            render = self.render_man (self, resource, request)
        if render.name == "HTML" :
            root        = resource.top
            Templateer  = root.Templateer
            t_name      = self.template_name
            if Templateer and t_name in Templateer.Template_Map :
                template = Templateer.get_template (t_name)
                context  = Templateer.Context \
                    ( exception       = self
                    , fatal_exception =
                        self if self.status_code >= 500 else None
                    , page            = resource
                    , nav_page        = resource
                    , NAV             = root
                    , request         = request
                    , response        = response
                    , template        = template
                    )
                with Templateer.GTW.LET (blackboard = dict ()) :
                    body = template.render (context)
            else :
                desc = _T (self.description)
                body = \
                    (  ("%s: %s" % (desc, pyk.text_type (self.message)))
                    if self.message else desc
                    )
        else :
            body = dict \
                ( self._kw
                , description = self.description
                )
            if self.message :
                body ["message"] = pyk.text_type (self.message)
        render (request, response, body)
    # end def _add_response_body

    def _add_response_headers (self, resource, request, response) :
        pass
    # end def _add_response_headers

    def __repr__ (self) :
        result  = [repr (self.__class__)]
        message = self.message
        if message :
            if not isinstance (message, pyk.string_types) :
                message = str (message)
            result.append (message)
        return " ".join (result)
    # end def __repr__

# end class Status

class Informational (Status) :
    """Base class for HTTP status classes indicating a provisional response [1xx]."""
# end class Informational

class Continue (Informational) :
    """The client SHOULD continue with its request."""

    status_code = 100

    _spec       = \
        """ This interim response is used to inform the client that the
            initial part of the request has been received and has not yet
            been rejected by the server. The client SHOULD continue by
            sending the remainder of the request or, if the request has
            already been completed, ignore this response. The server MUST
            send a final response after the request has been completed. See
            section 8.2.3 for detailed discussion of the use and handling of
            this status code.
        """

# end class Continue

class Switching_Protocols (Informational) :
    """The server understands and is willing to comply with the client's
       request, via the Upgrade message header field (section 14.42), for a
       change in the application protocol being used on this connection.
    """

    status_code = 101

    _spec       = \
        """ The server will switch protocols to those defined by the
            response's Upgrade header field immediately after the empty line
            which terminates the 101 response.

            The protocol SHOULD be switched only when it is advantageous to
            do so. For example, switching to a newer version of HTTP is
            advantageous over older versions, and switching to a real-time,
            synchronous protocol might be advantageous when delivering
            resources that use such features.
        """

# end class Switching_Protocols

class Successful (Status) :
    """Base class for HTTP status classes indicating successful completion [2xx]."""
# end class Successful

class OK (Successful) :
    """The request has succeeded."""

    status_code = 200

    _spec       = \
        """ The information returned with the response is dependent on the
            method used in the request, for example:

            GET an entity corresponding to the requested resource is sent in
            the response;

            HEAD the entity-header fields corresponding to the requested
            resource are sent in the response without any message-body;

            POST an entity describing or containing the result of the action;

            TRACE an entity containing the request message as received by the
            end server.
        """

# end class OK

class Created (Successful) :
    """The request has been fulfilled and resulted in a new resource being
       created.
    """

    status_code = 201

    _spec       = \
        """ The newly created resource can be referenced by the URI(s)
            returned in the entity of the response, with the most specific
            URI for the resource given by a Location header field. The
            response SHOULD include an entity containing a list of resource
            characteristics and location(s) from which the user or user agent
            can choose the one most appropriate. The entity format is
            specified by the media type given in the Content-Type header
            field. The origin server MUST create the resource before
            returning the 201 status code. If the action cannot be carried
            out immediately, the server SHOULD respond with 202 (Accepted)
            response instead.

            A 201 response MAY contain an ETag response header field
            indicating the current value of the entity tag for the requested
            variant just created, see section 14.19.
        """

# end class Created

class Accepted (Successful) :
    """The request has been accepted for processing, but the processing has
       not been completed.
    """

    status_code = 202

    _spec       = \
        """ The request might or might not eventually be acted upon, as it
            might be disallowed when processing actually takes place. There
            is no facility for re-sending a status code from an asynchronous
            operation such as this.

            The 202 response is intentionally non-committal. Its purpose is
            to allow a server to accept a request for some other process
            (perhaps a batch-oriented process that is only run once per day)
            without requiring that the user agent's connection to the server
            persist until the process is completed. The entity returned with
            this response SHOULD include an indication of the request's
            current status and either a pointer to a status monitor or some
            estimate of when the user can expect the request to be fulfilled.
        """

# end class Accepted

class Non_Authoritative_Information (Successful) :
    """The returned metainformation in the entity-header is not the
       definitive set as available from the origin server, but is gathered from
       a local or a third-party copy.
    """

    status_code = 203

    _spec       = \
        """ The set presented MAY be a subset or superset of the original
            version. For example, including local annotation information
            about the resource might result in a superset of the
            metainformation known by the origin server. Use of this response
            code is not required and is only appropriate when the response
            would otherwise be 200 (OK).
        """

# end class Non_Authoritative_Information

class No_Content (Successful) :
    """The server has fulfilled the request but does not need to return an
       entity-body, and might want to return updated metainformation.
    """

    status_code = 204

    _spec       = \
        """ The response MAY include new or updated metainformation in the
            form of entity-headers, which if present SHOULD be associated with
            the requested variant.

            If the client is a user agent, it SHOULD NOT change its document
            view from that which caused the request to be sent. This response
            is primarily intended to allow input for actions to take place
            without causing a change to the user agent's active document
            view, although any new or updated metainformation SHOULD be
            applied to the document currently in the user agent's active
            view.

            The 204 response MUST NOT include a message-body, and thus is
            always terminated by the first empty line after the header fields.
        """

# end class No_Content

class Reset_Content (Successful) :
    """The server has fulfilled the request and the user agent SHOULD reset
       the document view which caused the request to be sent.
    """

    status_code = 205

    _spec       = \
        """ This response is primarily intended to allow input for actions to
            take place via user input, followed by a clearing of the form in
            which the input is given so that the user can easily initiate
            another input action.

            The response MUST NOT include an entity.
        """

# end class Reset_Content

class Partial_Content (Successful) :
    """The server has fulfilled the partial GET request for the resource."""

    status_code = 206

    _spec       = \
        """ The request MUST have included a Range header field (section
            14.35) indicating the desired range, and MAY have included an
            If-Range header field (section 14.27) to make the request
            conditional.

            The response MUST include the following header fields:

                  - Either a Content-Range header field (section 14.16)
                    indicating the range included with this response, or a
                    multipart/byteranges Content-Type including Content-Range
                    fields for each part. If a Content-Length header field is
                    present in the response, its value MUST match the actual
                    number of OCTETs transmitted in the message-body.

                  - Date

                  - ETag and/or Content-Location, if the header would have
                    been sent in a 200 response to the same request

                  - Expires, Cache-Control, and/or Vary, if the field-value might
                    differ from that sent in any previous response for the same
                    variant

            If the 206 response is the result of an If-Range request that
            used a strong cache validator (see section 13.3.3), the response
            SHOULD NOT include other entity-headers. If the response is the
            result of an If-Range request that used a weak validator, the
            response MUST NOT include other entity-headers; this prevents
            inconsistencies between cached entity-bodies and updated headers.
            Otherwise, the response MUST include all of the entity-headers
            that would have been returned with a 200 (OK) response to the
            same request.
        """

# end class Partial_Content

class Redirection (Status) :
    """Base class for HTTP status classes indicating redirection [3xx]."""

    def __init__ (self, location, message = None, ** kw) :
        self.location = location
        self.__super.__init__ (message, ** kw)
    # end def __init__

    def _add_response_headers (self, resource, request, response) :
        self.__super._add_response_headers (resource, request, response)
        response.set_header ("Location", self.location)
    # end def _add_response_headers

# end class Redirection

class Multiple_Choices (Redirection) :
    """The requested resource corresponds to any one of a set of
       representations, each with its own specific location, and agent-driven
       negotiation information (section 12) is being provided so that the user
       (or user agent) can select a preferred representation and redirect its
       request to that location.
    """

    status_code = 300

    _spec       = \
        """ Unless it was a HEAD request, the response SHOULD include an
            entity containing a list of resource characteristics and
            location(s) from which the user or user agent can choose the one
            most appropriate. The entity format is specified by the media type
            given in the Content-Type header field. Depending upon the format
            and the capabilities of the user agent, selection of the most
            appropriate choice MAY be performed automatically. However, this
            specification does not define any standard for such automatic
            selection.

            If the server has a preferred choice of representation, it SHOULD
            include the specific URI for that representation in the Location
            field; user agents MAY use the Location field value for automatic
            redirection. This response is cacheable unless indicated
            otherwise.
        """

# end class Multiple_Choices

class Moved_Permanently (Redirection) :
    """The requested resource has been assigned a new permanent URI and any
       future references to this resource SHOULD use one of the returned URIs.
    """

    status_code = 301

    _spec       = \
        """ The new permanent URI SHOULD be given by the Location field in
            the response. Unless the request method was HEAD, the entity of the
            response SHOULD contain a short hypertext note with a hyperlink to
            the new URI(s).

            If the 301 status code is received in response to a request other
            than GET or HEAD, the user agent MUST NOT automatically redirect
            the request unless it can be confirmed by the user, since this
            might change the conditions under which the request was issued.

              Note: When automatically redirecting a POST request after
              receiving a 301 status code, some existing HTTP/1.0 user agents
              will erroneously change it into a GET request.
        """

# end class Moved_Permanently

class Found (Redirection) :
    """The requested resource resides temporarily under a different URI."""

    status_code = 302
    description = "Found (moved temporarily)"

    _spec       = \
        """ Since the redirection might be altered on occasion, the client
            SHOULD continue to use the Request-URI for future requests. This
            response is only cacheable if indicated by a Cache-Control or
            Expires header field.

            The temporary URI SHOULD be given by the Location field in the
            response. Unless the request method was HEAD, the entity of the
            response SHOULD contain a short hypertext note with a hyperlink
            to the new URI(s).

            If the 302 status code is received in response to a request other
            than GET or HEAD, the user agent MUST NOT automatically redirect
            the request unless it can be confirmed by the user, since this
            might change the conditions under which the request was issued.

              Note: RFC 1945 and RFC 2068 specify that the client is not
              allowed to change the method on the redirected request.
              However, most existing user agent implementations treat 302 as
              if it were a 303 response, performing a GET on the Location
              field-value regardless of the original request method. The
              status codes 303 and 307 have been added for servers that wish
              to make unambiguously clear which kind of reaction is expected
              of the client.

            http://insanecoding.blogspot.co.at/2014/02/http-308-incompetence-expected.html::

              Since 302 was being used in two different ways, two new codes
              were created, one for each technique, to ensure proper use in
              the future. 302 retained its definition, but with so many
              incorrect implementations out there, 302 should essentially
              never be used if you want to ensure correct semantics are
              followed, instead use 303 - See Other (processing, move on...),
              or 307 Temporary Redirect (The real version of 302).

              In all my experience working with HTTP over the past decade,
              I've found 301, 303, and 307 to be implemented and used
              correctly as defined in HTTP v1.1, with 302 still being used
              incorrectly as 303 (instead of 307 semantics), generally by PHP
              programmers. But as above, never use 302, as who knows what the
              browser will do with it.

              Since existing practice today is that 301, 303, and 307 are
              used correctly pretty much everywhere, if someone misuses it,
              they should be told to correct their usage or handling. 302 is
              still so misused till this day, it's a lost cause.

        """

# end class Found

class See_Other (Redirection) :
    """The response to the request can be found under a different URI and
       SHOULD be retrieved using a GET method on that resource.
    """

    cache_control = dict (no_cache = True)
    status_code   = 303

    _spec         = \
        """ This method exists primarily to allow the output of a
            POST-activated script to redirect the user agent to a selected
            resource. The new URI is not a substitute reference for the
            originally requested resource. The 303 response MUST NOT be cached,
            but the response to the second (redirected) request might be
            cacheable.

            The different URI SHOULD be given by the Location field in the
            response. Unless the request method was HEAD, the entity of the
            response SHOULD contain a short hypertext note with a hyperlink
            to the new URI(s).

              Note: Many pre-HTTP/1.1 user agents do not understand the 303
              status. When interoperability with such clients is a concern, the
              302 status code may be used instead, since most user agents react
              to a 302 response as described here for 303.

        """

# end class See_Other

class Not_Modified (Redirection) :
    """If the client has performed a conditional GET request and access is
       allowed, but the document has not been modified, the server SHOULD
       respond with this status code.
    """

    status_code = 304

    _spec       = \
        """ The 304 response MUST NOT contain a message-body, and thus is
            always terminated by the first empty line after the header fields.

            The response MUST include the following header fields:

            - Date, unless its omission is required by section 14.18.1

            If a clockless origin server obeys these rules, and proxies and
            clients add their own Date to any response received without one
            (as already specified by [RFC 2068], section 14.19), caches will
            operate correctly.

            - ETag and/or Content-Location, if the header would have been sent
              in a 200 response to the same request

            - Expires, Cache-Control, and/or Vary, if the field-value might
              differ from that sent in any previous response for the same
              variant

            If the conditional GET used a strong cache validator (see section
            13.3.3), the response SHOULD NOT include other entity-headers.
            Otherwise (i.e., the conditional GET used a weak validator), the
            response MUST NOT include other entity-headers; this prevents
            inconsistencies between cached entity-bodies and updated headers.

            If a 304 response indicates an entity not currently cached, then
            the cache MUST disregard the response and repeat the request
            without the conditional.

            If a cache uses a received 304 response to update a cache entry,
            the cache MUST update the entry to reflect any new field values
            given in the response.
        """

# end class Not_Modified

class Use_Proxy (Redirection) :
    """The requested resource MUST be accessed through the proxy given by the
       Location field.
    """

    status_code = 305

    _spec       = \
        """ The Location field gives the URI of the proxy. The recipient is
            expected to repeat this single request via the proxy.

            305 responses MUST only be generated by origin servers.

              Note: RFC 2068 was not clear that 305 was intended to redirect
              a single request, and to be generated by origin servers only.
              Not observing these limitations has significant security
              consequences.
        """

# end class Use_Proxy

class Temporary_Redirect (Redirection) :
    """The requested resource resides temporarily under a different URI."""

    cache_control = dict (no_cache = True)
    status_code   = 307

    _spec         = \
        """ Since the redirection MAY be altered on occasion, the client
            SHOULD continue to use the Request-URI for future requests. This
            response is only cacheable if indicated by a Cache-Control or
            Expires header field.

            The temporary URI SHOULD be given by the Location field in the
            response. Unless the request method was HEAD, the entity of the
            response SHOULD contain a short hypertext note with a hyperlink
            to the new URI(s) , since many pre-HTTP/1.1 user agents do not
            understand the 307 status. Therefore, the note SHOULD contain the
            information necessary for a user to repeat the original request
            on the new URI.

            If the 307 status code is received in response to a request other
            than GET or HEAD, the user agent MUST NOT automatically redirect
            the request unless it can be confirmed by the user, since this
            might change the conditions under which the request was issued.
        """

# end class Temporary_Redirect

class Error (Status) :
    """Base for for HTTP status classes indicating errors [4xx, 5xx]."""
# end class Error

class Client_Error (Error) :
    """Base for for HTTP status classes indicating client errors [4xx]."""
# end class Client_Error

class Bad_Request (Client_Error) :
    """The request could not be understood by the server due to malformed
       syntax. The client SHOULD NOT repeat the request without modifications.
    """

    status_code = 400

# end class Bad_Request

class Login_Required (Client_Error) :
    """The request requires user authentication. You need to login."""

    ### Sending back status code `401` to a browser results in the browser
    ### displaying its own ugly authorization dialog
    ###
    ### To avoid this we send back a `400` status code and a login form
    ### (for hysterical raisins, `template_name` is still 401)

    status_code   = 400
    template_name = 401

# end class Login_Required

class Unauthorized (Client_Error) :
    """The request requires user authentication."""

    status_code = 401
    realm       = "basic-auth"
    scheme      = "Basic"

    _spec       = \
        """ The response MUST include a WWW-Authenticate header field
            (section 14.47) containing a challenge applicable to the requested
            resource. The client MAY repeat the request with a suitable
            Authorization header field (section 14.8). If the request already
            included Authorization credentials, then the 401 response indicates
            that authorization has been refused for those credentials. If the
            401 response contains the same challenge as the prior response,
            and the user agent has already attempted authentication at least
            once, then the user SHOULD be presented the entity that was given
            in the response, since that entity might include relevant
            diagnostic information. HTTP access authentication is explained
            in "HTTP Authentication: Basic and Digest Access Authentication"
        """

    def _add_response_headers (self, resource, request, response) :
        self.__super._add_response_headers (resource, request, response)
        try :
            auth = self.auth
        except AttributeError :
            auth = '%s realm="%s"' % (self.scheme, self.realm)
        response.set_header ("WWW-Authenticate", auth)
    # end def _add_response_headers

# end class Unauthorized

class Forbidden (Client_Error) :
    """The server understood the request, but is refusing to fulfill it.
       Authorization will not help and the request SHOULD NOT be repeated.
    """

    status_code = 403

    _spec       = \
        """ If the request method was not HEAD and the server wishes to make
            public why the request has not been fulfilled, it SHOULD describe
            the reason for the refusal in the entity. If the server does not
            wish to make this information available to the client, the status
            code 404 (Not Found) can be used instead.
        """

# end class Forbidden

class Not_Found (Client_Error) :
    """The server has not found anything matching the Request-URI."""

    status_code = 404

    _spec       = \
        """ No indication is given of whether the condition is temporary or
            permanent. The 410 (Gone) status code SHOULD be used if the
            server knows, through some internally configurable mechanism,
            that an old resource is permanently unavailable and has no
            forwarding address. This status code is commonly used when the
            server does not wish to reveal exactly why the request has been
            refused, or when no other response is applicable.
        """

# end class Not_Found

class Method_Not_Allowed (Client_Error) :
    """The method specified in the Request-Line is not allowed for the
       resource identified by the Request-URI.
    """

    status_code = 405

    _spec       = \
        """ The response MUST include an Allow header containing a list of
            valid methods for the requested resource.
        """

    def _add_response_headers (self, resource, request, response) :
        self.__super._add_response_headers (resource, request, response)
        try :
            valid_methods = self.valid_methods
        except AttributeError :
            valid_methods = resource.SUPPORTED_METHODS
        response.set_header ("Allow", ", ".join (sorted (valid_methods)))
    # end def _add_response_headers

# end class Method_Not_Allowed

class Not_Acceptable (Client_Error) :
    """The resource identified by the request is only capable of generating
       response entities which have content characteristics not acceptable
       according to the accept headers sent in the request.
    """

    status_code = 406

    _spec       = \
        """ Unless it was a HEAD request, the response SHOULD include an
            entity containing a list of available entity characteristics and
            location(s) from which the user or user agent can choose the one
            most appropriate. The entity format is specified by the media
            type given in the Content-Type header field. Depending upon the
            format and the capabilities of the user agent, selection of the
            most appropriate choice MAY be performed automatically. However,
            this specification does not define any standard for such
            automatic selection.

              Note: HTTP/1.1 servers are allowed to return responses which
              are not acceptable according to the accept headers sent in the
              request. In some cases, this may even be preferable to sending
              a 406 response. User agents are encouraged to inspect the
              headers of an incoming response to determine if it is
              acceptable.

            If the response could be unacceptable, a user agent SHOULD
            temporarily stop receipt of more data and query the user for a
            decision on further actions.
        """

# end class Not_Acceptable

class Proxy_Authentication_Required (Unauthorized) :
    """This code is similar to 401 (Unauthorized), but indicates that the
       client must first authenticate itself with the proxy.
    """

    status_code = 407

    _spec       = \
        """ The proxy MUST return a Proxy-Authenticate header field (section
            14.33) containing a challenge applicable to the proxy for the
            requested resource. The client MAY repeat the request with a
            suitable Proxy-Authorization header field (section 14.34). HTTP
            access authentication is explained in "HTTP Authentication: Basic
            and Digest Access Authentication"
        """

# end class Proxy_Authentication_Required

class Request_Timeout (Client_Error) :
    """The client did not produce a request within the time that the server
       was prepared to wait. The client MAY repeat the request without
       modifications at any later time.
    """

    status_code = 408

# end class Request_Timeout

class Conflict (Client_Error) :
    """The request could not be completed due to a conflict with the current
       state of the resource.
    """

    status_code = 409

    _spec       = \
        """ This code is only allowed in situations where it is expected that
            the user might be able to resolve the conflict and resubmit the
            request. The response body SHOULD include enough information for
            the user to recognize the source of the conflict. Ideally, the
            response entity would include enough information for the user or
            user agent to fix the problem; however, that might not be
            possible and is not required.

            Conflicts are most likely to occur in response to a PUT request.
            For example, if versioning were being used and the entity being
            PUT included changes to a resource which conflict with those made
            by an earlier (third-party) request, the server might use the 409
            response to indicate that it can't complete the request. In this
            case, the response entity would likely contain a list of the
            differences between the two versions in a format defined by the
            response Content-Type.
        """

# end class Conflict

class Gone (Client_Error) :
    """The requested resource is no longer available at the server and no
       forwarding address is known.
    """

    status_code = 410

    _spec       = \
        """ This condition is expected to be considered permanent. Clients
            with link editing capabilities SHOULD delete references to the
            Request-URI after user approval. If the server does not know, or
            has no facility to determine, whether or not the condition is
            permanent, the status code 404 (Not Found) SHOULD be used
            instead. This response is cacheable unless indicated otherwise.

            The 410 response is primarily intended to assist the task of web
            maintenance by notifying the recipient that the resource is
            intentionally unavailable and that the server owners desire that
            remote links to that resource be removed. Such an event is common
            for limited-time, promotional services and for resources
            belonging to individuals no longer working at the server's site.
            It is not necessary to mark all permanently unavailable resources
            as "gone" or to keep the mark for any length of time -- that is
            left to the discretion of the server owner.
        """

# end class Gone

class Length_Required (Client_Error) :
    """The server refuses to accept the request without a defined
       Content-Length.
    """

    status_code = 411

    _spec       = \
        """ The client MAY repeat the request if it adds a valid
            Content-Length header field containing the length of the
            message-body in the request message.
        """

# end class Length_Required

class Precondition_Failed (Client_Error) :
    """The precondition given in one or more of the request-header fields
       evaluated to false when it was tested on the server.
    """

    status_code = 412

    _spec       = \
        """ This response code allows the client to place preconditions on
            the current resource metainformation (header field data) and thus
            prevent the requested method from being applied to a resource
            other than the one intended.
        """

# end class Precondition_Failed

class Request_Entity_Too_Large (Client_Error) :
    """The server is refusing to process a request because the request entity
       is larger than the server is willing or able to process.
    """

    status_code = 413

    _spec       = \
        """ The server MAY close the connection to prevent the client from
            continuing the request.

            If the condition is temporary, the server SHOULD include a Retry-
            After header field to indicate that it is temporary and after
            what time the client MAY try again.
        """

    def _add_response_headers (self, resource, request, response) :
        self.__super._add_response_headers (resource, request, response)
        try :
            retry_after = self.retry_after
        except AttributeError :
            pass
        else :
            response.set_header ("Retry-After", retry_after)
    # end def _add_response_headers

# end class Request_Entity_Too_Large

class Request_URI_Too_Long (Client_Error) :
    """The server is refusing to service the request because the Request-URI
       is longer than the server is willing to interpret.
    """

    status_code = 414

    _spec       = \
        """ This rare condition is only likely to occur when a client has
            improperly converted a POST request to a GET request with long
            query information, when the client has descended into a URI
            "black hole" of redirection (e.g., a redirected URI prefix that
            points to a suffix of itself), or when the server is under attack
            by a client attempting to exploit security holes present in some
            servers using fixed-length buffers for reading or manipulating
            the Request-URI.
        """

# end class Request_URI_Too_Long

class Unsupported_Media_Type (Client_Error) :
    """The server is refusing to service the request because the entity of
       the request is in a format not supported by the requested resource for
       the requested method.
    """

    status_code = 415

# end class Unsupported_Media_Type

class Requested_Range_Not_Satisfiable (Client_Error) :
    """A server SHOULD return a response with this status code if a request
       included a Range request-header field (section 14.35), and none of the
       range-specifier values in this field overlap the current extent of the
       selected resource, and the request did not include an If-Range
       request-header field.
    """

    status_code = 416

    _spec       = \
        """ (For byte-ranges, this means that the first- byte-pos of all of
            the byte-range-spec values were greater than the current length of
            the selected resource.)

            When this status code is returned for a byte-range request, the
            response SHOULD include a Content-Range entity-header field
            specifying the current length of the selected resource (see
            section 14.16). This response MUST NOT use the
            multipart/byteranges content- type.
        """

# end class Requested_Range_Not_Satisfiable

class Expectation_Failed (Client_Error) :
    """The expectation given in an Expect request-header field (see section
       14.20) could not be met by this server, or, if the server is a proxy,
       the server has unambiguous evidence that the request could not be met
       by the next-hop server.
    """

    status_code = 417

# end class Expectation_Failed

class Server_Error (Error) :
    """Base for for HTTP status classes indicating server errors [5xx]."""
# end class Server_Error

class Internal_Server_Error (Server_Error) :
    """The server encountered an unexpected condition which prevented it from
       fulfilling the request.
    """

    status_code = 500

# end class Internal_Server_Error

class Not_Implemented (Server_Error) :
    """The server does not support the functionality required to fulfill the
       request.
    """
    status_code = 501

    _spec       = \
        """ This is the appropriate response when the server does not
            recognize the request method and is not capable of supporting it
            for any resource.
        """

# end class Not_Implemented

class Bad_Gateway (Server_Error) :
    """The server, while acting as a gateway or proxy, received an invalid
       response from the upstream server it accessed in attempting to fulfill
       the request.
    """

    status_code = 502

# end class Bad_Gateway

class Service_Unavailable (Server_Error) :
    """The server is currently unable to handle the request due to a
       temporary overloading or maintenance of the server.
    """

    status_code = 503
    retry_after = CAL.Date_Time_Delta (minutes = 3)

    _spec       = \
        """ The implication is that this is a temporary condition which will
            be alleviated after some delay. If known, the length of the delay
            MAY be indicated in a Retry-After header. If no Retry-After is
            given, the client SHOULD handle the response as it would for a
            500 response.

              Note: The existence of the 503 status code does not imply that
              a server must use it when becoming overloaded. Some servers may
              wish to simply refuse the connection.
        """

    def _add_response_headers (self, resource, request, response) :
        self.__super._add_response_headers (resource, request, response)
        try :
            retry_after = self.retry_after
        except AttributeError :
            pass
        else :
            if isinstance (retry_after, CAL.Date_Time_Delta) :
                retry_after = CAL.Date_Time ().as_utc () + retry_after
            if retry_after is not None :
                response.set_header ("Retry-After", retry_after)
    # end def _add_response_headers

# end class Service_Unavailable

class Gateway_Timeout (Server_Error) :
    """The server, while acting as a gateway or proxy, did not receive a
       timely response from the upstream server specified by the URI (e.g.
       HTTP, FTP, LDAP) or some other auxiliary server (e.g. DNS) it needed
       to access in attempting to complete the request.
    """

    status_code = 504

# end class Gateway_Timeout

class HTTP_Version_Not_Supported (Server_Error) :
    """The server does not support, or refuses to support, the HTTP protocol
       version that was used in the request message.
    """

    status_code = 505

    _spec       = \
        """ The server is indicating that it is unable or unwilling to
            complete the request using the same major version as the client,
            as described in section 3.1, other than with this error message.
            The response SHOULD contain an entity describing why that version
            is not supported and what other protocols are supported by that
            server.
        """

# end class HTTP_Version_Not_Supported

if __name__ != "__main__" :
    GTW.RST._Export_Module ()
### __END__ GTW.RST.HTTP_Status
