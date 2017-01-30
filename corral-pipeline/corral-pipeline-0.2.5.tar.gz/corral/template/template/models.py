#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created at ${timestamp} by corral ${version}


# =============================================================================
# DOCS
# =============================================================================

"""${project_name} database models

"""

# =============================================================================
# IMPORTS
# =============================================================================

from corral import db


# =============================================================================
# MODELS (Put your models below)
# =============================================================================

class Example(db.Model):

    __tablename__ = 'Example'

    id = db.Column(db.Integer, primary_key=True)
