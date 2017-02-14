from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import sys

from foorti import fetch_list

def test_list():
    bears = fetch_list('bears')
    assert len(bears) == 0

    bears.right_append('grizzly')
    assert bears.list_len == 1
    assert bears[0] == 'grizzly'
    assert bears[-1] == 'grizzly'

    for bear in bears:
        assert bear == 'grizzly'

    assert 'grizzly' in bears

    assert list(bears) == ['grizzly', 'white bear', 'nice bear', 'polar bear', 'gummy bear']

    assert bears[1:2] == ['white bear']
    assert bears[2:4] == ['nice bear', 'polar bear']
    assert bears[:2] == ['grizzly', 'white bear']
    assert bears[-2:] == ['polar bear', 'gummy bear']
    assert bears[10:20] == []

    bears.right_remove('grizzly')
    assert 'grizzly' not in bears

    bears.clear()
    assert bears.list_len == 0

    N = 512
    for i in range(N):
        bears.right_append(i)
    assert bears.list_len == N

    back = [e for e in bears]
    assert back.list_len == N

    
def test_list_trim():
    deers = fetch_list('deers')

    for i in range(0, 100):
        deers.right_append('rudolf_%s' % i)

    assert deers.list_len == 100

    deers.list_trim(0, 5)

    assert deers.list_len == 6

    assert deers[0] == 'rudolf_0'
    assert deers[1] == 'rudolf_1'

    
if __name__ == '__main__':
    test_list()    
    test_list_trim