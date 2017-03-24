'''Tests for ColumnarRecords methods and associated helper functions'''

from builtins import zip
from future.utils import lzip

import numpy as np

from columnar_records import ColumnarRecords, from_records, from_recarray, get_index_groups

L1 = [[1,2,3,4], ['a', 'b', 'c', 'd']]
L2 = [[1,2,3,4], ['d', 'c', 'b', 'a']]
N2 = ['numbers', 'letters']
L3 = [[1, 1, 2, 2, 3, 3, 4, 4, 4],
     ['a', 'b', 'c', 'a', 'b', 'c', 'a', 'b', 'c'],
     [float(i) / 9 for i in range(9)]]

def test_tolist_1():
    cr = ColumnarRecords(L1)
    assert(cr.tolist() == L1)

def test_indexing_1():
    cr = ColumnarRecords(L1)
    assert(cr[0].tolist() == [1, 'a'])

def test_eq_1():
    cr = ColumnarRecords(L1)
    assert(np.array_equal(cr == cr,
           [True]*4))

def test_ne_1():
    cr = ColumnarRecords(L1)
    assert(np.array_equal(cr != cr,
           [False]*4))

def test_array_equal_1():
    cr = ColumnarRecords(L1)
    crB = ColumnarRecords(L1)
    assert(cr.array_equal(
           crB))

def test_slicing_1():
    cr = ColumnarRecords(L1)
    assert(cr[1:3].array_equal(
           [i[1:3] for i in L1]))

def test_slicing_2_with_strings():
    cr = ColumnarRecords(L1)
    assert(cr[['f0', 'f1']].array_equal(
           cr))

def test_slicing_3_reverse():
    cr = ColumnarRecords(L1)
    assert(cr[::-1].array_equal(
           [i[::-1] for i in L1]))

def test_slicing_4():        # really push indexing, etc
    cr = ColumnarRecords(L1)
    assert(cr[None][None][:, :, ::-2][0, 0].array_equal(
           [i[::-2] for i in L1]))

def test_sort_1():
    cr = ColumnarRecords(L1)
    assert(cr[::-1].sort().array_equal(
           cr))

def test_from_records_1():
    cr = ColumnarRecords(L1)
    assert(from_records(lzip(*L1)).array_equal(
           cr))
    
def test_recarray_1():
    cr = ColumnarRecords(L1)
    a = from_recarray(np.rec.fromarrays(L1))
    assert a.array_equal(cr)
    
def test_from_recarray_2():
    cr = ColumnarRecords(L1)
    assert(from_recarray(np.rec.fromarrays(L1)).array_equal(
           cr))

def test_iter_1():
    cr = ColumnarRecords(L1)
    assert([i for i in cr] == lzip(*L1)) # test __iter__
    
    
def test_sort_2():
    cr2 = ColumnarRecords(L2, names=N2)
    assert(cr2.sort().array_equal(
           cr2))

def test_sort_3():
    cr2 = ColumnarRecords(L2, names=N2)
    assert(cr2.sort(['numbers', 'letters']).array_equal(
           cr2))

def test_sort_4():
    cr2 = ColumnarRecords(L2, names=N2)
    assert(cr2.sort(['letters', 'numbers']).array_equal(
           ColumnarRecords([i[::-1] for i in L2], N2)))
    
def test_get_index_groups_1():
    cr3 = ColumnarRecords(L3, names=['i', 'a', 'f'])
    cr_a = cr3.get_index_groups(['a'])
    nu_a = get_index_groups(cr3['a'])
    assert(np.array_equal(cr_a[0]['a'], nu_a[0]))
    assert(np.array_equal(cr_a[1], nu_a[1]))
    
def test_get_index_groups_2():
    cr3 = ColumnarRecords(L3, names=['i', 'a', 'f'])
    cr_ia = cr3.get_index_groups(['i', 'a'])
    nu_ia = get_index_groups(cr3[['i', 'a']].torecords())
    assert(cr_ia[0].array_equal(from_recarray(nu_ia[0])))
    assert(np.array_equal(cr_ia[1], nu_ia[1]))
    
def test_get_index_groups_3():
    cr3 = ColumnarRecords(L3, names=['i', 'a', 'f'])
    cr_ai = cr3.get_index_groups(['a', 'i'])
    nu_ai = get_index_groups(cr3[['a', 'i']].torecords())
    assert(cr_ai[0].array_equal(from_recarray(nu_ai[0])))
    assert(np.array_equal(cr_ai[1], nu_ai[1]))
    
def test_get_index_groups_4():
    cr3 = ColumnarRecords(L3, names=['i', 'a', 'f'])
    cr_ia = cr3.get_index_groups(['i', 'a'])
    cr_ai = cr3.get_index_groups(['a', 'i'])
    
    assert(not cr_ia[0].array_equal(
               cr_ai[0]))
    assert(not np.array_equal(cr_ia[1],
                              cr_ai[1]))

def test_setslice_1():
    cr = ColumnarRecords(L3, names=['i', 'a', 'f'])
    insert = ColumnarRecords([i[:2] for i in L3], names=['i', 'a', 'f'])
    cr[1:3] = insert
    assert(cr[1].array_equal(cr[0]))


def test_setitem_1():
    cr = ColumnarRecords(L1)
    cr['f0'] = [5,6,7,8]
    assert(cr.array_equal(
           [[5,6,7,8], L1[1]]))

def test_setitem_2():
    cr = ColumnarRecords(L3, names=['i', 'a', 'f'])
    cr['f', 'a'] = [[float(i) for i in range(9)], list('thereare9')]
    assert(cr.array_equal(
           ColumnarRecords([L3[0], list('thereare9'), np.arange(9)],
                           names=['i', 'a', 'f'])))

def test_setitem_3():
    cr = ColumnarRecords(L3, names=['i', 'a', 'f'])
    cr['a', 'f'] = ColumnarRecords([np.arange(9), list('thereare9')], names=['f', 'a'])
    assert(cr.array_equal(
           ColumnarRecords([L3[0], list('thereare9'), np.arange(9)],
                           names=['i', 'a', 'f'])))

def test_setitem_4():
    cr = ColumnarRecords(L3, names=['i', 'a', 'f'])
    cr[:4] = cr[-4:]
    assert(cr[:4].array_equal(
           cr[-4:]))

def test_setitem_5():
    cr = ColumnarRecords(L3, names=['i', 'a', 'f'])
    cr[4] = cr[0]
    assert(cr[4].array_equal(
           cr[0]))

def test_setitem_6():
    cr = ColumnarRecords(L3, names=['i', 'a', 'f'])
    cr[[1, 4]] = cr[[0, 2]]
    assert(cr[[1, 4]].array_equal(
           cr[[0, 2]]))

if __name__ == '__main__':
    test_tolist_1()
    test_indexing_1()
    test_eq_1()
    test_ne_1()
    test_array_equal_1()
    test_slicing_1()
    test_slicing_2_with_strings()
    test_slicing_3_reverse()
    test_slicing_4()
    test_sort_1()
    test_from_records_1()
    test_recarray_1()
    test_from_recarray_2()
    test_iter_1()
    test_sort_2()
    test_sort_3()
    test_sort_4()
    test_get_index_groups_1()
    test_get_index_groups_2()
    test_get_index_groups_3()
    test_get_index_groups_4()
    test_setslice_1()
    test_setitem_1()
    test_setitem_2()
    test_setitem_3()
    test_setitem_4()
    test_setitem_5()
    test_setitem_6()

    
    
