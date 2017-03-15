from test import Test
from nose.tools import assert_equal

# Tests Test class


class TestTest:

    def __init__(self):
        self.default_url_prefix = "http://search.unbxdapi.com"
        self.tests = [
            {"test": [
                {
                    "name": "XML Search API Validation for test search API",
                }, {
                    "url": "http://search.unbxdapi.com/d9db733454a3fe3b16a3df9dc3ba4b33/testing-u1436766985789/search?q=black%20tote&wt=xml",
                }, {
                    "group": "SAMPLE TEST",
                }, {
                    "method": "GET",
                }, {
                    "validators": [
                        {
                            "compare": {
                                "xpath": "/response/lst[@name='searchMetaData']/int[@name='status']",
                                "comparator": "eq",
                                "type": "text",
                                "expected": "0",
                            },
                        },
                    ],
                },
            ], "assert": True,
            }, { "test" : [
                {
                    "name": "XML Search API Validation for test search API",
                }, {
                    "url": "http://search.unbxdapi.com/d9db733454a3fe3b16a3df9dc3ba4b33/testing-u1436766985789/search?q=black%20tote&wt=xml",
                }, {
                    "group": "SAMPLE TEST",
                }, {
                    "method": "GET",
                }, {
                    "validators": [
                        {
                            "compare": {
                                "xpath": "/response/result/@numberOfProducts",
                                "comparator": "eq",
                                "type": "element",
                                "expected": "7",
                            },
                        },
                    ],
                },
            ], "assert" : True,
            }, { "test": [
                {
                    "name": "XML Search API Validation for test search API",
                }, {
                    "url": "http://search.unbxdapi.com/d9db733454a3fe3b16a3df9dc3ba4b33/testing-u1436766985789/search?q=black%20tote&wt=xml",
                }, {
                    "group": "SAMPLE TEST",
                }, {
                    "method": "GET",
                }, {
                    "validators": [
                        {
                            "compare": {
                                "xpath": "(//product/str[@name='uniqueId'])[2]",
                                "comparator": "eq",
                                "type": "text",
                                "expected": "0141253513101",
                            },
                        },
                    ],
                },
            ], "assert" : True
            }, { "test" : [
                {
                    "name": "XML Search API Validation for test search API",
                }, {
                    "url": "http://search.unbxdapi.com/d9db733454a3fe3b16a3df9dc3ba4b33/testing-u1436766985789/search?q=black%20tote&wt=xml",
                }, {
                    "group": "SAMPLE TEST",
                }, {
                    "method": "GET",
                }, {
                    "validators": [
                        {
                            "compare": {
                                "xpath": "(//product/str[@name='StyleCode'])[4]",
                                "comparator": "eq",
                                "type": "text",
                                "expected": '014-1253-5122-68',
                            },
                        },
                    ],
                },
            ], "assert": True
            }
        ]

    def __load_data__(self, test_data):
        return_data = {}
        for td in test_data:
            if 'name' in td:
                return_data['name'] = td['name']
            if 'url' in td:
                return_data['url'] = td['url']
            if 'group' in td:
                return_data['group'] = td['group']
            if 'method' in td:
                return_data['method'] = td['method']
            if 'validators' in td:
                return_data['validators'] = td['validators']
        return return_data

    def test_init(self):
        data = [
            {
                "name": "XML Search API Validation for test search API",
            }, {
                "url": "/d9db733454a3fe3b16a3df9dc3ba4b33/testing-u1436766985789/search?q=black%20tote&wt=xml",
            }, {
                "group": "SAMPLE TEST",
            }, {
                "method": "GET",
            }, {
                "validators": [
                    {
                        "compare": {
                            "xpath": "/response/lst[@name='searchMetaData']/int[@name='status']",
                            "comparator": "eq",
                            "type": "text",
                            "expected": '0',
                        },
                    },
                ],
            },
        ]

        t = Test(data)
        test_data = self.__load_data__(data)
        assert_equal(t.to_string(), test_data['name'] + " "
                     + self.default_url_prefix + test_data['url']
                     + " " + test_data['group'] + " " + test_data['method']
                     + " " + 'compare' + " " + "xpath" + " "
                     + test_data['validators'][0]['compare']['xpath'] + " "
                     + test_data['validators'][0]['compare']['comparator'] + " "
                     + test_data['validators'][0]['compare']['type'])

    def test_run(self):
        for test in self.tests:
            t = Test(test['test'])
            assert_equal(t.run(), test['assert'])
