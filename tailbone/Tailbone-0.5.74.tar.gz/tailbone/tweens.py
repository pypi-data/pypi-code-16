# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2016 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Tween Factories
"""

from __future__ import unicode_literals, absolute_import

from sqlalchemy.exc import OperationalError
from transaction.interfaces import TransientError


def sqlerror_tween_factory(handler, registry):
    """
    Produces a tween which will convert ``sqlalchemy.exc.OperationalError``
    instances (caused by database server restart) into a retryable
    ``transaction.interfaces.TransientError`` instance, so that a second
    attempt may be made to connect to the database before really giving up.

    .. note::
       This tween alone is not enough to cause the transaction to be retried;
       it only marks the error as being *retryable*.  If you wish more than one
       attempt to be made, you must define the ``tm.attempts`` setting within
       your Pyramid app configuration.  For more info see `Retrying`_.

       .. _Retrying: http://docs.pylonsproject.org/projects/pyramid_tm/en/latest/#retrying
    """

    def sqlerror_tween(request):
        try:
            response = handler(request)
        except OperationalError as error:
            if error.connection_invalidated:
                raise TransientError(str(error))
            raise
        return response

    return sqlerror_tween
