# -*- coding: utf-8 -*-

from concurrent.futures import ThreadPoolExecutor


def pmap(fn, arr, n=4):
    with ThreadPoolExecutor(n) as e:
        return list(e.map(fn, arr))
