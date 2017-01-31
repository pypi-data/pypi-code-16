from ftw.builder import builder_registry
from ftw.builder.dexterity import DexterityBuilder
from ftw.subsite.tests import builders
from ftw.simplelayout.tests import builders


class AddressBlockBuilder(DexterityBuilder):
    portal_type = 'ftw.addressblock.AddressBlock'

builder_registry.register('sl addressblock', AddressBlockBuilder)
