#!/usr/bin/env python

import unittest

import isoprene_pumpjack.utils.neo_to_d3 as neo_to_d3

class MockNeoLink(object):
    def __init__(self):
        self.id = '58bf0614e5568802aedd8d88'
        self.start = 'b2b08c572ab54540a02546c049c1e620'
        self.end = '8e8fc8c945d6484396ac33b50d6797e6'
        self.type = 'excepteur'
        self._items_dict = {
            "company": "DOGSPA",
            "email": "maura.perry@dogspa.me",
            "phone": "+1 (869) 553-3698",
            "address": "117 Kane Street, Dowling, New Jersey, 6443"
        }
        
    def items(self):
        for k, v in self._items_dict.iteritems():
            yield k, v


class TestNeoToD3(unittest.TestCase):
    def test_neo_link_to_d3_link(self):
        neo_link = MockNeoLink()
        d3_link = neo_to_d3.neo_link_to_d3_link(neo_link)
        
        self.assertEqual(d3_link['id'], '58bf0614e5568802aedd8d88')
        self.assertEqual(d3_link['source'], 'b2b08c572ab54540a02546c049c1e620')
        self.assertEqual(d3_link['target'], '8e8fc8c945d6484396ac33b50d6797e6')
        self.assertEqual(d3_link['labels'], ['excepteur'])
        self.assertEqual(d3_link['props'], {
            "company": "DOGSPA",
            "email": "maura.perry@dogspa.me",
            "phone": "+1 (869) 553-3698",
            "address": "117 Kane Street, Dowling, New Jersey, 6443"
        })
