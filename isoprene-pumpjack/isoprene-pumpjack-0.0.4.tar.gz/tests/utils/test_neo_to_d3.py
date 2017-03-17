#!/usr/bin/env python

import unittest

import isoprene_pumpjack.utils.neo_to_d3 as neo_to_d3

# With thanks to http://www.json-generator.com/ for the mock data

class MockNeoObject(object):
    def items(self):
        for k, v in self._items_dict.iteritems():
            yield k, v

class MockNeoLink(MockNeoObject):
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
        
class MockNeoNode(MockNeoObject):
    def __init__(self):
        self.id = '119fac6967a14297b066d102d8ae0ddf'
        self.labels = ["culpa", "deserunt"]
        self._items_dict = {
            "company": "GORGANIC",
            "email": "kellerpacheco@gorganic.com",
            "phone": "+1 (953) 451-3487",
            "address": "767 Times Placez, Rockingham,"
        }


class TestNeoToD3Utils(unittest.TestCase):
    def test_dict_deduping(self):
        list_of_dicts = [
            {
                "guid": "19539ee450ac406f8ab59a59da77e6e7",
                "eyeColor": "brown",       
            },
            {
                "guid": "992a96b75c1a461184f64615bca8a20e",
                "eyeColor": "hazel",       
            },
            {
                "guid": "6809bb15ca514a568ad74d310ce4d915",
                "eyeColor": "blue",       
            }
        ]
        list_of_dicts_duplicated = [
            list_of_dicts[0],
            list_of_dicts[0],
            list_of_dicts[2],
            list_of_dicts[1],
            list_of_dicts[0],            
            list_of_dicts[2],            
        ]
        deduped_dict_list = neo_to_d3.dedupe_dict_list(list_of_dicts_duplicated, "guid")
        self.assertEqual(len(deduped_dict_list), len(list_of_dicts))
        self.assertItemsEqual(list_of_dicts, deduped_dict_list)


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
    
    def test_neo_node_to_d3_node(self):
        neo_node = MockNeoNode()
        d3_node = neo_to_d3.neo_node_to_d3_node(neo_node)
        
        self.assertEqual(d3_node['id'], '119fac6967a14297b066d102d8ae0ddf')
        self.assertEqual(d3_node['labels'], ["culpa", "deserunt"])
        self.assertEqual(d3_node['props'], {
            "company": "GORGANIC",
            "email": "kellerpacheco@gorganic.com",
            "phone": "+1 (953) 451-3487",
            "address": "767 Times Placez, Rockingham,"
        })
