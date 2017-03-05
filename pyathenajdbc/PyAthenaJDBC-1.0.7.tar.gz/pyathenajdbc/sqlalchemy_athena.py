# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from sqlalchemy.engine import default


class AthenaDialect(default.DefaultDialect):
    name = 'athena'
    driver = 'jdbc'

    pass
