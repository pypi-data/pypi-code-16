from comparator import XMLComparator
from nose.tools import assert_equal


class TestXMLCompartor():

    def __init__(self):
        self.test_cases = [
            {
                "response_content": '<?xml version="1.0" encoding="UTF-8"?><note><to>Tove</to><from>Jani</from><heading>Reminder</heading><body>Don\'t forget me this weekend!</body></note>',
                "properties": {
                    "xpath": "/note/to",
                    "comparator": "eq",
                    "type": "text",
                    "expected": "Tove",
                },
                "assert": True,
            },
            {
                "response_content": '<?xml version="1.0" encoding="UTF-8"?><note><to>Tove</to><from>Jani</from><heading>Reminder</heading><body>Don\'t forget me this weekend!</body></note>',
                "properties": {
                    "xpath": "/note/from",
                    "comparator": "ne",
                    "type": "text",
                    "expected": "Tove",
                },
                "assert": True,
            },
            {
                "response_content": '<?xml version="1.0" encoding="UTF-8"?><note><to attr="name">Tove</to><from attr="name">Jani</from><heading content="subject" type="reminder">Reminder</heading><body content="body_text" type="reminder">Don\'t forget me this weekend!</body></note>',
                "properties": {
                    "xpath": "/note/to/@attr",
                    "comparator": "eq",
                    "type": "element",
                    "expected": "name",
                },
                "assert": True,
            },
            {
                "response_content": '<?xml version="1.0" encoding="UTF-8"?><note><to attr="name">Tove</to><from attr="name">Jani</from><heading content="subject" type="reminder">Reminder</heading><body content="body_text" type="reminder">Don\'t forget me this weekend!</body></note>',
                "properties": {
                    "xpath": "//heading/@content",
                    "comparator": "eq",
                    "type": "element",
                    "expected": "subject",
                },
                "assert": True,
            },
        ]

    def test_init(self):
        nick = 'xpath'
        xpath = '//A/B/[@name=\"abc\"]'
        condition = 'eq'
        _type = 'tag'
        expected = 'expected_value'

        init_property = {
            "xpath": xpath,
            "comparator": condition,
            "type": _type,
            "expected": expected,
        }

        x = XMLComparator(xpath, init_property)

        assert_equal(x.to_string(), nick + " " + xpath + " " + condition
                     + " " + _type)

    def test_compare(self):
        """ Compare Tests """
        for test in self.test_cases:
            init_property = test['properties']
            x = XMLComparator(init_property['xpath'], init_property)
            res = x.compare(test['response_content'])
            assert_equal(test["assert"], res)
