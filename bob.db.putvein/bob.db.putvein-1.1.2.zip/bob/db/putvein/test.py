#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import nose.tools
from .query import Database


def _query_simple_protocol_tests(protocol):
    db = Database()

    objs = db.objects(protocol)
    nose.tools.eq_(len(objs), 1800) # number of images in the protocol

    objs = db.objects(protocol, kinds='palm')
    nose.tools.eq_(len(objs), 900) # number of palm images in the protocol

    objs = db.objects(protocol, kinds='wrist')
    nose.tools.eq_(len(objs), 900) # number of wrist images in the protocol

    objs = db.objects(protocol, groups='train')
    nose.tools.eq_(len(objs), 600) # number of train images in the protocol

    objs = db.objects(protocol, groups='dev')
    nose.tools.eq_(len(objs), 600) # number of dev images in the protocol

    objs = db.objects(protocol, groups='eval')
    nose.tools.eq_(len(objs), 600) # number of dev eval in the protocol

    objs = db.objects(protocol, kinds='palm', groups='train')
    nose.tools.eq_(len(objs), 300) # number of palm train images in the protocol

    objs = db.objects(protocol, kinds='palm', groups='dev')
    nose.tools.eq_(len(objs), 300) # number of palm dev images in the protocol

    objs = db.objects(protocol, kinds='palm', groups='eval')
    nose.tools.eq_(len(objs), 300) # number of palm dev eval in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='train')
    nose.tools.eq_(len(objs), 300) # number of wrist train images in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='dev')
    nose.tools.eq_(len(objs), 300) # number of wrist dev images in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='eval')
    nose.tools.eq_(len(objs), 300) # number of wrist dev eval in the protocol

    objs = db.objects(protocol, kinds='palm', groups='dev', purposes='enroll')
    nose.tools.eq_(len(objs), 100) # number of palm dev enroll images in the protocol

    objs = db.objects(protocol, kinds='palm', groups='dev', purposes='probe')
    nose.tools.eq_(len(objs), 200) # number of palm dev probe images in the protocol

    objs = db.objects(protocol, kinds='palm', groups='eval', purposes='enroll')
    nose.tools.eq_(len(objs), 100) # number of palm dev enroll eval in the protocol

    objs = db.objects(protocol, kinds='palm', groups='eval', purposes='probe')
    nose.tools.eq_(len(objs), 200) # number of palm dev probe eval in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='dev', purposes='enroll')
    nose.tools.eq_(len(objs), 100) # number of wrist dev enroll images in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='dev', purposes='probe')
    nose.tools.eq_(len(objs), 200) # number of wrist dev probe images in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='eval', purposes='enroll')
    nose.tools.eq_(len(objs), 100) # number of wrist eval enroll in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='eval', purposes='probe')
    nose.tools.eq_(len(objs), 200) # number of wrist eval probe in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='eval', purposes='probe', ids=[26])
    nose.tools.eq_(len(objs), 8) # number of wrist eval probe in the protocol for client #26

    if protocol == 'L':
        nose.tools.eq_(objs[0].make_path(), 'Wrist/o_026/Left/Series_2/W_o026_L_S2_Nr1.bmp')
    else:
        nose.tools.eq_(objs[0].make_path(), 'Wrist/o_026/Right/Series_2/W_o026_R_S2_Nr1.bmp')

    for obj in objs:
        nose.tools.eq_(obj.get_client_id(), 26)
        nose.tools.eq_(obj.is_mirrored(), False)


def _query_combined_protocol_tests(protocol):
    db = Database()

    objs = db.objects(protocol)
    nose.tools.eq_(len(objs), 7200) # number of images in the protocol

    objs = db.objects(protocol, kinds='palm')
    nose.tools.eq_(len(objs), 3600) # number of palm images in the protocol

    objs = db.objects(protocol, kinds='wrist')
    nose.tools.eq_(len(objs), 3600) # number of wrist images in the protocol

    objs = db.objects(protocol, groups='train')
    nose.tools.eq_(len(objs), 1200) # number of train images in the protocol

    objs = db.objects(protocol, groups='dev')
    nose.tools.eq_(len(objs), 1200) # number of dev images in the protocol

    objs = db.objects(protocol, groups='eval')
    nose.tools.eq_(len(objs), 1200) # number of dev eval in the protocol

    objs = db.objects(protocol, kinds='palm', groups='train')
    nose.tools.eq_(len(objs), 600) # number of palm train images in the protocol

    objs = db.objects(protocol, kinds='palm', groups='dev')
    nose.tools.eq_(len(objs), 600) # number of palm dev images in the protocol

    objs = db.objects(protocol, kinds='palm', groups='eval')
    nose.tools.eq_(len(objs), 600) # number of palm dev eval in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='train')
    nose.tools.eq_(len(objs), 600) # number of wrist train images in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='dev')
    nose.tools.eq_(len(objs), 600) # number of wrist dev images in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='eval')
    nose.tools.eq_(len(objs), 600) # number of wrist dev eval in the protocol

    objs = db.objects(protocol, kinds='palm', groups='dev', purposes='enroll')
    nose.tools.eq_(len(objs), 200) # number of palm dev enroll images in the protocol

    objs = db.objects(protocol, kinds='palm', groups='dev', purposes='probe')
    nose.tools.eq_(len(objs), 400) # number of palm dev probe images in the protocol

    objs = db.objects(protocol, kinds='palm', groups='eval', purposes='enroll')
    nose.tools.eq_(len(objs), 200) # number of palm dev enroll eval in the protocol

    objs = db.objects(protocol, kinds='palm', groups='eval', purposes='probe')
    nose.tools.eq_(len(objs), 400) # number of palm dev probe eval in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='dev', purposes='enroll')
    nose.tools.eq_(len(objs), 200) # number of wrist dev enroll images in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='dev', purposes='probe')
    nose.tools.eq_(len(objs), 400) # number of wrist dev probe images in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='eval', purposes='enroll')
    nose.tools.eq_(len(objs), 200) # number of wrist eval enroll in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='eval', purposes='probe')
    nose.tools.eq_(len(objs), 400) # number of wrist eval probe in the protocol

    objs = db.objects(protocol, kinds='wrist', groups='dev', purposes='probe', ids=[26])
    nose.tools.eq_(len(objs), 8) # number of wrist dev probe in the protocol for client #26

    if protocol == 'LR':
        nose.tools.eq_(objs[0].make_path(), 'Wrist/o_026/Left/Series_2/W_o026_L_S2_Nr1.bmp')
    else:
        nose.tools.eq_(objs[0].make_path(), 'Wrist/o_026/Right/Series_2/W_o026_R_S2_Nr1.bmp')

    for obj in objs:
        nose.tools.eq_(obj.get_client_id(), 26)
        nose.tools.eq_(obj.is_mirrored(), False)

    objs = db.objects(protocol, kinds='wrist', groups='eval', purposes='probe', ids=[76])
    nose.tools.eq_(len(objs), 8) # number of wrist eval probe in the protocol for client #76

    if protocol == 'LR':
        nose.tools.eq_(objs[0].make_path(), 'Wrist/o_026/Right/Series_2/W_o026_R_S2_Nr1.bmp')
    else:
        nose.tools.eq_(objs[0].make_path(), 'Wrist/o_026/Left/Series_2/W_o026_L_S2_Nr1.bmp')

    for obj in objs:
        nose.tools.eq_(obj.get_client_id(), 76)
        nose.tools.eq_(obj.is_mirrored(), True)


def test_query_L_protocol():
    _query_simple_protocol_tests('L')


def test_query_R_protocol():
    _query_simple_protocol_tests('R')


def test_query_LR_protocol():
    _query_combined_protocol_tests('LR')


def test_query_RL_protocol():
    _query_combined_protocol_tests('RL')


def test_dumplist():
  from bob.db.base.script.dbmanage import main
  nose.tools.eq_(main('putvein dumplist --protocol=L --self-test'.split()), 0)

