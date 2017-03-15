from validator import CompareValidator
from nose.tools import assert_equal


class TestCompareValidator:

    def test_init(self):
        test_set = [{
            'data': {
                'xpath': '/note/to/@attr',
                'comparator': 'eq',
                'type': 'text',
                'expected': 'Jones'
            },
            'string': 'compare xpath /note/to/@attr eq text',
        }, {
            'data': {
                'xpath': '//body/@content',
                'comparator': 'ne',
                'type': 'text',
                'expected': 'body_text',
            },
            'string': 'compare xpath //body/@content ne text',
        }]

        for test in test_set:
            c = CompareValidator(test['data'])
            assert_equal(test['string'], c.to_string())

    def test_validate(self):
        test_set = [
            {
                'response_content': '<?xml version="1.0" encoding="UTF-8"?><note><to attr="name">Tove</to><from attr="name">Jani</from><heading content="subject" type="reminder">Reminder</heading><body content="body_text" type="reminder">Don\'t forget me this weekend!</body></note>',
                'data': {
                    'xpath': '/note/to/@attr',
                    'comparator': 'eq',
                    'type': 'element',
                    'expected': 'name',
                    },
                'assert': True
                },
            {
                'response_content': '<?xml version="1.0" encoding="UTF-8"?><note><to attr="name">Tove</to><from attr="name">Jani</from><heading content="subject" type="reminder">Reminder</heading><body content="body_text" type="reminder">Don\'t forget me this weekend!</body></note>',
                'data': {
                    'xpath': '//heading/@type',
                    'comparator': 'ne',
                    'type': 'element',
                    'expected': 'subject',
                    },
                'assert': True
                },
            {
                'response_content': '<?xml version="1.0" encoding="UTF-8"?><note><to attr="name">Tove</to><from attr="name">Jani</from><heading content="subject" type="reminder">Reminder</heading><body content="body_text" type="reminder">Don\'t forget me this weekend!</body></note>',
                'data': {
                    'xpath': '/note/body/@type',
                    'comparator': 'eq',
                    'type': 'element',
                    'expected': 'reminder',
                    },
                'assert': True
                },
            {
                'response_content': '<?xml version="1.0" encoding="UTF-8"?><note><to attr="name">Tove</to><from attr="name">Jani</from><heading content="subject" type="reminder">Reminder</heading><body content="body_text" type="reminder">Don\'t forget me this weekend!</body></note>',
                'data': {
                    'xpath': '/note//body/@content',
                    'comparator': 'eq',
                    'type': 'element',
                    'expected': 'body_text',
                    },
                'assert': True
                },
            {
                'response_content': '<?xml version="1.0" encoding="UTF-8"?><note><to attr="name">Tove</to><from attr="name">Jani</from><heading content="subject" type="reminder">Reminder</heading><body content="body_text" type="reminder">Don\'t forget me this weekend!</body></note>',
                'data': {
                    'xpath': '/note//to',
                    'comparator': 'eq',
                    'type': 'text',
                    'expected': 'Tove',
                    },
                'assert': True
                },
            ]

        for test in test_set:
            v = CompareValidator(test['data'])
            assert_equal(test['assert'], v.validate(test['response_content']))
