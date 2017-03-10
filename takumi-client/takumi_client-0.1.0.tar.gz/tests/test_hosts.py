# -*- coding: utf-8 -*-


def test_list_hosts():
    from takumi_client.hosts import ListHosts

    conf = {'hosts': [('localhost', 1000), ('localhost', 2000)]}
    target = {}
    h = ListHosts(conf, target)
    h.update()
    assert target == {('localhost', 1000): 0, ('localhost', 2000): 0}
