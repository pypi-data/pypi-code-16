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
Model for inventory batches
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr

from rattail.db.model import Base, BatchMixin, ProductBatchRowMixin


class InventoryBatch(BatchMixin, Base):
    """
    Batch for product inventory counts; note that this requires a data file.
    """
    __tablename__ = 'batch_inventory'
    __batchrow_class__ = 'InventoryBatchRow'
    batch_key = 'inventory'

    @declared_attr
    def __table_args__(cls):
        return cls.__default_table_args__() + (
            sa.ForeignKeyConstraint(['handheld_batch_uuid'], ['batch_handheld.uuid'],
                                    name='batch_inventory_fk_handheld_batch'),
            )

    handheld_batch_uuid = sa.Column(sa.String(length=32), nullable=True)

    handheld_batch = orm.relationship(
        'HandheldBatch',
        doc="""
        Reference to the handheld batch from which this inventory batch originated.
        """,
        backref=orm.backref('inventory_batch', uselist=False, doc="""
        Reference to the inventory batch to which this handheld batch was converted.
        """))

    mode = sa.Column(sa.Integer(), nullable=True, doc="""
    Specifies the "mode" for the inventory count batch, i.e. how the count data
    should ultimately be interpreted/applied.
    """)


class InventoryBatchRow(ProductBatchRowMixin, Base):
    """
    Rows for inventory batches.
    """
    __tablename__ = 'batch_inventory_row'
    __batch_class__ = InventoryBatch

    STATUS_OK = 1
    STATUS_PRODUCT_NOT_FOUND = 2

    STATUS = {
        STATUS_OK:                      "ok",
        STATUS_PRODUCT_NOT_FOUND:       "product not found",
    }

    cases = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Case quantity for the record.
    """)

    units = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Unit quantity for the record.
    """)
