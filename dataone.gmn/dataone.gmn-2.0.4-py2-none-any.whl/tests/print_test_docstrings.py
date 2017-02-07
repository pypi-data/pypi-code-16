#!/usr/bin/env python

import inspect
import re

import gmn_integration_tests

method_list = inspect.getmembers(
  gmn_integration_tests.GMNIntegrationTests,
  predicate=inspect.ismethod
)

for name_str, member_obj in method_list:
  if name_str.startswith('test_'):
    doc_str = re.sub(r'\s+', ' ', member_obj.__doc__).strip()
    print '{:<15}{}'.format(name_str, doc_str)


