# pcontracts_example_2.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0702

import pexdoc.pcontracts

@pexdoc.pcontracts.new_contract('Only one exception')
def custom_contract_a(name):
    msg = pexdoc.pcontracts.get_exdesc()
    if not name:
        raise ValueError(msg)

@pexdoc.pcontracts.new_contract(ex1='Empty name', ex2='Invalid name')
def custom_contract_b(name):
    msg = pexdoc.pcontracts.get_exdesc()
    if not name:
        raise ValueError(msg['ex1'])
    elif name.find('[') != -1:
        raise ValueError(msg['ex2'])
