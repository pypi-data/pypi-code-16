# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.RST.MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.RST.MOM.__doc__
#
# Purpose
#    Documentation for package GTW.RST.MOM
#
# Revision Dates
#    14-Jul-2012 (CT) Creation
#     4-Dec-2012 (CT) Add bib-refs [Amu11] and [WPR10]
#    13-Mar-2013 (CT) Improve documentation
#    16-Apr-2013 (CT) Add more documentation about AQ expressions
#     3-May-2013 (CT) Add `META`
#     4-Oct-2013 (CT) Add `fields` and `add_fields`
#    27-Mar-2014 (CT) Document `E_Type.OPTIONS`
#    12-Oct-2016 (CT) Remove spurious import
#    12-Oct-2016 (CT) Use `#>>`, not `>>>`, to avoid failing tests
#                     (the code is meant to illustrate but doesn't run!)
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

__doc__ = """
.. moduleauthor:: Christian Tanzer <tanzer@swing.co.at>

Package `GTW.RST.MOM`
======================

This package provides classes implementing a generic `RESTful web service`_
(see also [RiR07]_) for applications based on the MOM meta object model (see
[Tan95]_).

A RESTful web service is a set of URLs, each URL referring to a specific
resource and supporting one or more of the `standard HTTP methods`_. At a
minimum, each resource supports the safe HTTP methods ``GET``, ``HEAD``, and
``OPTIONS``. Some resources also support HTTP methods with side effects, such
as ``DELETE``, ``POST``, and ``PUT``.

The ``OPTIONS`` methods returns the list of HTTP methods supported by the
specified resource.

Depending on the setup, a RESTful web service implemented by ``GTW.RST.MOM``
provides access to one or more databases, each holding a different instance
of a MOM model. In the following documentation, we'll assume the simplest
case of just a single database, with the web service mapped to ``/`` ignoring
the protocol and domain.

``Scope``
----------

For a specific database, the top URL of the RESTful web service refers to a
so-called ``Scope``. The scope provides access to all essential entity types,
aka ``E-Types``, that comprise the object model. The scope does not support
HTTP methods with side effects.

Use the HTTP method ``GET`` to retrieve the list of ``E-Types`` defined by the
``scope``. ``GET`` returns a ``JSON`` object with the attribute ``entries`` listing
the URLs or URL fragments of the scopes ``e-types``.

For instance, the elided result of a ``GET`` request for the URL ``/``
might look like::

        { 'entries' :
            [ '/MOM-Id_Entity'
            , '/MOM-Link'
            , '/MOM-Link1'
            , '/MOM-Link2'
            , '/MOM-Object'
            , '/PAP-Address'
            , '/PAP-Subject'
            , '/PAP-Company'
            , '/PAP-Email'
            , '/PAP-Phone'
            , '/PAP-Person'
            , '/PAP-Subject_has_Property'
            , '/PAP-Subject_has_Address'
            , '/PAP-Company_has_Address'
            , '/PAP-Subject_has_Email'
            , '/PAP-Company_has_Email'
            , '/PAP-Subject_has_Phone'
            , '/PAP-Company_has_Phone'
            , '/PAP-Person_has_Address'
            , '/PAP-Person_has_Email'
            , '/PAP-Person_has_Phone'
            ]
        }

``E-Type``
------------

An ``E-Type`` describes a specific essential entity type of a MOM model. The
RESTful resource for a ``e-type`` allows read and write access to all instances
of the ``e-type`` in question.

``GET``
~~~~~~~~

Use the HTTP method ``GET`` to retrieve the list of instances of the ``e-type``.

* ``GET`` without any parameters returns a ``JSON`` object with the attribute
  ``entries`` listing the URLs of the instances of the
  ``e-type``.

  For instance (using the Python package `requests`_)::

    #>> requests.get ("/PAP-Person").json
    { 'entries' :
        [ '/PAP-Person/1'
        , '/PAP-Person/2'
        , '/PAP-Person/3'
        ]
    }

* ``GET`` with the query parameter ``brief`` returns a `JSON`_ object
  with the attribute ``entries`` listing the permanent ids, aka ``pids``, of the
  instances of the ``e-type``.

  For instance::

    #>> requests.get ("/PAP-Person?brief").json
    { 'entries' :
        [ 1
        , 2
        , 3
        ]
    , 'url_template' : '/PAP-Person/{entry}'
    }

* ``GET`` with the query parameter ``verbose`` returns a `JSON`_ object
  with the attributes:

  - ``attribute_names``: the list of attribute names for instances of the
    ``e-type``.

  - ``entries``: the list of instances; for each instance a `JSON`_ object
    containing:

    * ``pid``: permanent id of instance.

    * ``cid``: id of last change.

    * ``attributes``: `JSON`_ object mapping attribute names to values.

      - if the value of an attribute refers to an instance of another ``e-type``,
        only the pid and the url of the instance are returned, unless the
        ``GET`` request contained the query parameter ``closure``, in which case
        a nested `JSON`_ object with the information about the nested object
        is returned here.

    * ``type_name``: name of essential entity type.

    * ``url``: URL of resource referring to this instance.

  For instance::

    #>> requests.get ("/PAP-Person?verbose").json
    { 'attribute_names' :
        [ 'last_name'
        , 'first_name'
        , 'middle_name'
        , 'title'
        , 'lifetime.start'
        , 'lifetime.finish'
        , 'sex'
        ]
    , 'entries' :
        [ { 'attributes' :
              { 'first_name' : 'christian'
              , 'last_name' : 'tanzer'
              , 'middle_name' : ''
              , 'title' : ''
              }
          , 'cid' : 1
          , 'pid' : 1
          , 'type_name' : 'PAP.Person'
          , 'url' : '/PAP-Person/1'
          }
        ...
        ]
    }

You can use additional query parameters to restrict the number of instances
returned or to search for specific instances. Possible query parameters are:

- ``ckd``: Return cooked values for attributes of types supported by
  Javascript, i.e., ``int``, ``float``, and ``string``. The cooked attribute
  values are returned in a ``JSON`` object with name ``attributes``.

  If neither ``ckd`` nor ``raw`` is specified as query parameter, per default
  cooked values are returned.

  For instance::

    #>> requests.get ("/PAP-Person/1").json
    { 'attributes' :
        { 'first_name' : 'christian'
        , 'last_name' : 'tanzer'
        , 'middle_name' : ''
        , 'title' : ''
        }
    , 'cid' : 1
    , 'pid' : 1
    , 'type_name' : 'PAP.Person'
    , 'url' : '/v1/PAP-Person/1'
    }

    #>> requests.get ("/PAP-Person/1?ckd").json
    { 'attributes' :
        { 'first_name' : 'christian'
        , 'last_name' : 'tanzer'
        , 'middle_name' : ''
        , 'title' : ''
        }
    , 'cid' : 1
    , 'pid' : 1
    , 'type_name' : 'PAP.Person'
    , 'url' : '/v1/PAP-Person/1'
    }

- ``raw``: Return raw values for all attributes. The raw attribute values  are
  returned in a `JSON`_ object with name ``attributes_raw``.

  Depending on the attribute type, raw values can differ from cooked values.
  For instance, for attributes like ``last_name`` and ``first_name`` of the
  essential type ``PAP.Person`` the cooked value is derived from the raw value
  by converting it to lower case. For attribute values denoting frequencies,
  the raw value is a string that can contain a unit like ``kHz`` or ``GHz``,
  while the cooked value is a floating point value normalized to ``Hz``.

  If an attribute value is to be shown in an UI, the raw value is generally
  asked for; OTOH, if an attribute value is to be used for computations, the
  cooked value is the one to use.

  For instance::

    #>> requests.get ("/PAP-Person/1?raw").json
    { 'attributes_raw' :
        { 'first_name' : 'Christian'
        , 'last_name' : 'Tanzer'
        , 'middle_name' : ''
        , 'title' : ''
        }
    , 'cid' : 1
    , 'pid' : 1
    , 'type_name' : 'PAP.Person'
    , 'url' : '/v1/PAP-Person/1'
    }

    #>> requests.get ("/PAP-Person/1?ckd&raw").json
    { 'attributes' :
        { 'first_name' : 'christian'
        , 'last_name' : 'tanzer'
        , 'middle_name' : ''
        , 'title' : ''
        }
    , 'attributes_raw' :
        { 'first_name' : 'Christian'
        , 'last_name' : 'Tanzer'
        , 'middle_name' : ''
        , 'title' : ''
        }
    , 'cid' : 1
    , 'pid' : 1
    , 'type_name' : 'PAP.Person'
    , 'url' : '/v1/PAP-Person/1'
    }

- ``closure``: Return nested objects as ``JSON`` objects, not just references.

  * For any nested object, only the first occurence is returned in full,
    subsequent occurences just contain ``pid`` and ``url``.

- ``count``: Return just the count, not the list, of instances.

- ``fields``: Select the database columns to include in output.

- ``add_fields``: Select additional fields for the output; you can specify
  any of the query attributes supported by the e-type in question.

- ``limit``: Restrict the number of returned instances to the value specified.

- ``offset``: Number of first instance to return; can be used together with
  ``limit`` and ``order_by`` to iterate over all instances.

- ``order_by``: Criteria used to sort the ``results``; comma separated list of
  attribute names and/or ``pid``. Each criterion may be preceded by ``-`` to
  sort the results in descending direction for that criterion.

- ``strict``: Limit the results to strict instances of the e-type in question,
  i.e., don't include instances of derived e-types. If you specify ``strict``
  for a partial, aka abstract, e-type you'll get an empty list of results.

- ``AQ``: restrict results to those matching the attribute query specified. The
  value for this query parameter is a comma-separated tuple of attribute
  name, operator, and value::

      AQ=<attribute-name>,<operator>,<value>

  The possible attribute-names depend on the type queried and are documented
  for each type. A GET request to a type-specific resource of
  the REST Api will return a link to the documentation of that type as a
  link-header with ``rel=doc``.

  Possible operators include:

  * ``EQ``: equal

  * ``NE``: not equal

  * ``GE``: greater than or equal

  * ``GT``: greater than

  * ``LE``: less than or equal

  * ``LT``: less than

  * ``IN``: attribute value is member of the set specified as query value

  * ``CONTAINS``: attribute value contains the specified query value

  * ``ENDSWITH``: attribute value ends with the specified query value

  * ``STARTSWITH``: attribute value starts with the specified query value

  If you specify more than one AQ expression, they are ANDed
  together.

- ``FIRST``: Results start with first instance, according to ``order_by``.

- ``LAST``: Results end with last instance, according to ``order_by``.

- ``META``: Return meta information about creation and last_change of objects.

  For each instance, the response includes the JSON objects ``creation`` and
  ``last_change``; both of these objects have a ``date`` field, and if known
  a ``user`` field.


``OPTIONS``
~~~~~~~~~~~

In addition to the list of supported HTTP methods, the ``OPTIONS`` method of
``E-Type`` resources returns the documentation for the ``e-type`` represented
as JSON.

``POST``
~~~~~~~~~

Use the HTTP method ``POST`` to create a new instance of the ``e-type``. The
request body for the ``POST`` must be a `JSON`_ object with the attribute
``attributes_raw`` which in turn must be a `JSON`_ object that maps attribute
names to attribute values. The POSTing of cooked attribute values is not
supported.

For instance::

    #>> cargo = json.dumps (
    ...   dict
    ...     ( attributes_raw = dict
    ...         ( last_name   = "Dog"
    ...         , first_name  = "Snoopy"
    ...         , middle_name = "the"
    ...         , lifetime    = dict (start = "20001122")
    ...         )
    ...     )
    ... )
    #>> headers = { "Content-Type": "application/json" }
    #>> requests.post ("/PAP-Person", data = cargo, headers = headers).json
    { 'attributes_raw' :
        { 'first_name' : 'Snoopy'
        , 'last_name' : 'Dog'
        , 'lifetime' :
            [
              [ 'start'
              , '2000-11-22'
              ]
            ]
        , 'middle_name' : 'the'
        , 'title' : ''
        }
    , 'cid' : 17
    , 'pid' : 17
    , 'type_name' : 'PAP.Person'
    , 'url' : '/PAP-Person/17'
    }

A successful ``POST`` request returns a `JSON`_ object describing the newly
created instance. This `JSON`_ object has the same format as the result of a
``GET`` request for the instance.

``Instance``
--------------

The RESTful resource for an instance allows read and write access to the
instance. For HTTP methods with side effects, you need to pass the ``cid`` of
the instance as returned by a ``GET`` method.

``GET``
~~~~~~~~

Use the HTTP method ``GET`` to retrieve the value of the instance. ``GET``
returns a `JSON`_ object with the same structure as a ``verbose`` ``GET``
applied to the resource of the instance's e-type; the query arguments
``fields``, ``add_fields``, ``META``, and ``RELS`` can be used here, too.

For instance::

    #>> requests.get ("/PAP-Person/1?raw")
    { 'attributes_raw' :
        { 'first_name' : 'Christian'
        , 'last_name' : 'Tanzer'
        , 'middle_name' : ''
        , 'title' : ''
        }
    , 'cid' : 1
    , 'pid' : 1
    , 'type_name' : 'PAP.Person'
    , 'url' : '/PAP-Person/1'
    }

    #>> requests.get ("/PAP-Person/1?raw&META")
    { 'attributes_raw' :
        { 'first_name' : 'Christian'
        , 'last_name' : 'Tanzer'
        , 'middle_name' : ''
        , 'title' : ''
        }
    , 'cid' : 1
    , 'creation' :
        { 'date' : '2013-05-03 16:23:53', 'user' : 'rsc@runtux.com' }
    , 'last_change' :
        { 'date' : '2013-05-03 16:34:42', 'user' : 'rsc@runtux.com'  }
    , 'pid' : 1
    , 'type_name' : 'PAP.Person'
    , 'url' : '/PAP-Person/1'
    }

``PUT``
~~~~~~~~

Use the HTTP method ``PUT`` to change the value of an instance. The
request body for the ``PUT`` must be a `JSON`_ object with the attributes:

- ``cid``: the id of the last change of the instance, as returned by a previous
  ``GET`` (or possibly ``POST``) request.

  If the ``cid`` of the instance has changed in the meantime, the ``PUT`` request
  will fail with a HTTP status code of 409.

- ``attributes_raw``: a ``JSON`` object that maps attribute names to
  changed attribute values (in raw form). Attributes not listed in
  ``attributes_raw`` are not changed by the ``PUT`` request.

``DELETE``
~~~~~~~~~~~~

Use the HTTP method ``DELETE`` to remove the instance from the database; this
will also remove all links to the instance in question to preserve
referential integrity. You need to pass ``cid`` as query parameter. If the
``cid`` of the instance has changed in the meantime, the ``DELETE`` request will
fail with a HTTP status code of 409.

.. _`RESTful web service`: http://en.wikipedia.org/wiki/Representational_State_Transfer
.. _`REST`: http://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm
.. _`standard HTTP methods`: http://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol#Request_methods
.. _`JSON`: http://en.wikipedia.org/wiki/JSON
.. _`requests`: http://pypi.python.org/pypi/requests

Bibliography
--------------

.. [Amu11] Amundsen, M.: 2011, Building Hypermedia APIs with HTML5 and Node.
           ISBN 978-1-4493-0656-4
           http://oreilly.com/catalog/0636920020530

.. [Fie00] Fielding, R.T.: 2000, Architectural Styles and the Design of
           Network-based Software Architectures; Chapter 5, Representational
           State Transfer (REST).
           http://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm

.. [Fie08] Fielding, R.T.: 2008, REST APIs must be hypertext-driven.
           http://roy.gbiv.com/untangled/2008/rest-apis-must-be-hypertext-driven

.. [RiR07] Richardson, L., Ruby, S.: 2007, RESTful Web Services.
           ISBN 978-0-596-52926-0
           http://oreilly.com/catalog/9780596529260

.. [Tan95] Tanzer, C.: 1995, Remarks on Object-Oriented Modelling of
           Associations. Journal of Object-Oriented Programming, Vol. 7, No.
           9, February 1995, pp. 43-46.

.. [WPR10] Webber, J., Parastatidis, S., Robinson, I.: 2010, REST in Practice;
           Hypermedia and Systems Architecture.
           ISBN 978-1-4493-9494-3
           http://oreilly.com/catalog/9780596805838

"""

### __END__ GTW.RST.MOM.__doc__
