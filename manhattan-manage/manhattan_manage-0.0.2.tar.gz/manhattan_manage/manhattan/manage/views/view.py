"""
Generic view document chain.
"""

from manhattan.chains import Chain, ChainMgr

from . import factories

__all__ = ['view_chains']


# Define the chains
view_chains = ChainMgr()

# GET
view_chains['get'] = Chain([
    'authenticate',
    'get_document',
    'decorate',
    'render_template'
    ])


# Define the links
view_chains.set_link(factories.authenticate())
view_chains.set_link(factories.get_document('view'))
view_chains.set_link(factories.decorate('view'))
view_chains.set_link(factories.render_template('view'))