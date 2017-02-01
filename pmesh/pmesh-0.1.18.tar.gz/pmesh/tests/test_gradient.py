from mpi4py_test import MPITest
from numpy.testing import assert_array_equal
from numpy.testing import assert_allclose
from numpy.testing import assert_almost_equal

from pmesh.pm import ParticleMesh, RealField, ComplexField
from pmesh import window
import numpy

def perturb(comp, mode, value):
    comp = comp.copy()
    old = comp.cgetitem(mode)
    new = comp.csetitem(mode, value + old)
    return new - old, comp

def perturb_pos(pos, ind, value, comm):
    pos = pos.copy()
    start = sum(comm.allgather(pos.shape[0])[:comm.rank])
    end = sum(comm.allgather(pos.shape[0])[:comm.rank + 1])
    if ind[0] >= start and ind[0] < end:
        old = pos[ind[0] - start, ind[1]]
        coord = pos[ind[0]-start].copy()
        pos[ind[0] - start, ind[1]] = old + value
        new = pos[ind[0] - start, ind[1]]
    else:
        old = 0
        new = 0
        coord = 0
    diff = comm.allreduce(new - old)

    return diff, pos, comm.allreduce(coord)
def get_pos(pos, ind, comm):
    start = sum(comm.allgather(pos.shape[0])[:comm.rank])
    end = sum(comm.allgather(pos.shape[0])[:comm.rank + 1])
    if ind[0] >= start and ind[0] < end:
        old = pos[ind[0] - start, ind[1]]
    else:
        old = 0
    return comm.allreduce(old)

@MPITest([1, 4])
def test_c2r_gradient(comm):
    pm = ParticleMesh(BoxSize=8.0, Nmesh=[4, 4], comm=comm, dtype='f8')

    real = pm.generate_whitenoise(1234, mode='real')
    comp = real.r2c()

    def objective(comp):
        real = comp.c2r()
        obj = (real.value ** 2).sum()
        return comm.allreduce(obj)

    grad_real = RealField(pm)
    grad_real[...] = real[...] * 2
    grad_comp = ComplexField(pm)
    grad_comp = grad_real.c2r_gradient(grad_real)
    grad_comp.decompress_gradient(grad_comp)

    ng = []
    ag = []
    ind = []
    dx = 1e-7
    for ind1 in numpy.ndindex(*(list(grad_comp.cshape) + [2])):
        dx1, c1 = perturb(comp, ind1, dx)
        ng1 = (objective(c1) - objective(comp)) / dx
        ag1 = grad_comp.cgetitem(ind1) * dx1 / dx
        comm.barrier()
        ng.append(ng1)
        ag.append(ag1)
        ind.append(ind1)

    assert_allclose(ng, ag, rtol=1e-5)

@MPITest([1, 2])
def test_readout_gradient(comm):
    pm = ParticleMesh(BoxSize=8.0, Nmesh=[4, 4], comm=comm, dtype='f8', method='cic')

    real = pm.generate_whitenoise(1234, mode='real')

    def objective(real, pos, layout):
        value = real.readout(pos, layout=layout)
        obj = (value ** 2).sum()
        return comm.allreduce(obj)

    pos = numpy.array(numpy.indices(real.shape), dtype='f4').reshape(real.value.ndim, -1).T
    pos += real.start
    # avoid sitting at the pmesh points
    # cic gradient is zero on them, the numerical gradient fails.
    pos += 0.5
    pos *= pm.BoxSize / pm.Nmesh

    layout = pm.decompose(pos)

    obj = objective(real, pos, layout)
    value = real.readout(pos, layout=layout)
    grad_value = value * 2
    grad_real, grad_pos = real.readout_gradient(pos, btgrad=grad_value, layout=layout)

    ng = []
    ag = []
    ind = []
    dx = 1e-7
    for ind1 in numpy.ndindex(*grad_real.cshape):
        dx1, r1 = perturb(real, ind1, dx)
        ng1 = (objective(r1, pos, layout) - obj)/dx
        ag1 = grad_real.cgetitem(ind1) * dx1 / dx
        # print (dx1, dx, ind1, ag1, ng1)
        ng.append(ng1)
        ag.append(ag1)
        ind.append(ind1)

    assert_allclose(ng, ag, rtol=1e-5)

    # FIXME
    ng = []
    ag = []
    ind = []
    dx = 1e-7
    for ind1 in numpy.ndindex((real.csize, real.ndim)):
        dx1, pos1, old = perturb_pos(pos, ind1, dx, comm)
        layout1 = pm.decompose(pos1)
        ng1 = (objective(real, pos1, layout1) - obj)/dx
        ag1 = get_pos(grad_pos, ind1, comm) * dx1 / dx
        # print ('pos', old, ind1, 'a', ag1, 'n', ng1)
        ng.append(ng1)
        ag.append(ag1)
        ind.append(ind1)

    assert_allclose(ng, ag, rtol=1e-5)

@MPITest([1, 4])
def test_cdot_independent(comm):
    pm = ParticleMesh(BoxSize=8.0, Nmesh=[4, 4], comm=comm, dtype='f8')

    comp1 = pm.generate_whitenoise(1234, mode='complex')
    comp2 = pm.generate_whitenoise(1235, mode='complex')

    def objective(comp1, comp2):
        return comp1.cdot(comp2, independent=True)

    norm = comp1.cdot(comp1, independent=True)
    norm_check = 0
    for ind1 in [(0, 0), (0, 1), (0, 2),
                 (1, 0), (1, 1), (1, 2),
                 (2, 0), (2, 1), (2, 2),
                 (3, 0), (3, 1), (3, 2),]:
        if ind1 == (3, 0): continue
        if ind1 == (3, 2): continue
        norm_check += abs(comp1.cgetitem(ind1)) ** 2
    assert_allclose(norm, norm_check)

    grad_comp2 = comp1.cdot_gradient(gcdot=1.0, independent=True)
    grad_comp1 = comp2.cdot_gradient(gcdot=1.0, independent=True)

    ng = []
    ag = []
    ind = []
    dx = 1e-7
    for ind1 in numpy.ndindex(*(list(comp1.cshape) + [2])):
        dx1, c1 = perturb(comp1, ind1, dx)
        ng1 = (objective(c1, comp2) - objective(comp1, comp2)) / dx
        ag1 = grad_comp1.cgetitem(ind1) * dx1 / dx
        print (ind1, 'a', ag1, 'n', ng1)
        comm.barrier()
        ng.append(ng1)
        ag.append(ag1)
        ind.append(ind1)

    assert_allclose(ng, ag, rtol=1e-5)

@MPITest([1, 4])
def test_cdot_dependent(comm):
    pm = ParticleMesh(BoxSize=8.0, Nmesh=[4, 4], comm=comm, dtype='f8')

    comp1 = pm.generate_whitenoise(1234, mode='complex')
    comp2 = pm.generate_whitenoise(1235, mode='complex')

    def objective(comp1, comp2):
        return comp1.cdot(comp2, independent=False)

    norm = comp1.cdot(comp1, independent=False)
    norm_check = 0
    for ind1 in [(0, 0), (0, 1), (0, 2),
                 (1, 0), (1, 1), (1, 2),
                 (2, 0), (2, 1), (2, 2),
                 (3, 0), (3, 1), (3, 2),]:
        factor = 1
        if ind1 in [(0, 1), (1, 1), (2, 1), (3, 1) ]:
            factor = 2
        norm_check += abs(comp1.cgetitem(ind1)) ** 2 * factor

    assert_allclose(norm, norm_check)

@MPITest([1, 4])
def test_cdot_grad_dependent(comm):
    pm = ParticleMesh(BoxSize=8.0, Nmesh=[8, 8], comm=comm, dtype='f8')

    comp1 = pm.generate_whitenoise(1234, mode='complex')
    comp2 = pm.generate_whitenoise(1235, mode='complex')

    def objective(comp1, comp2):
        return comp1.cdot(comp2, independent=False)

    grad_comp2 = comp1.cdot_gradient(gcdot=1.0, independent=False)
    grad_comp1 = comp2.cdot_gradient(gcdot=1.0, independent=False)

    ng = []
    ag = []
    ind = []
    dx = 1e-7
    for ind1 in numpy.ndindex(*(list(comp1.cshape) + [2])):
        dx1, c1 = perturb(comp1, ind1, dx)
        ng1 = (objective(c1, comp2) - objective(comp1, comp2)) / dx
        ag1 = grad_comp1.cgetitem(ind1) * dx1 / dx
        print (ind1, 'a', ag1, 'n', ng1)
        comm.barrier()
        ng.append(ng1)
        ag.append(ag1)
        ind.append(ind1)

    assert_allclose(ng, ag, rtol=1e-5)

@MPITest([1, 4])
def test_cdot_grad_independent(comm):
    pm = ParticleMesh(BoxSize=8.0, Nmesh=[8, 8], comm=comm, dtype='f8')

    comp1 = pm.generate_whitenoise(1234, mode='complex')
    def metric(k):
        return 3.

    def objective(comp1):
        return comp1.cdot(comp1, metric=metric, independent=True)

    grad_comp1 = comp1.cdot_gradient(gcdot=2.0, metric=metric, independent=True)

    ng = []
    ag = []
    ind = []
    dx = 1e-7
    for ind1 in numpy.ndindex(*(list(comp1.cshape) + [2])):
        dx1, c1 = perturb(comp1, ind1, dx)
        ng1 = (objective(c1) - objective(comp1)) / dx
        ag1 = grad_comp1.cgetitem(ind1) * dx1 / dx
        print (ind1, 'a', ag1, 'n', ng1)
        comm.barrier()
        ng.append(ng1)
        ag.append(ag1)
        ind.append(ind1)

    assert_allclose(ng, ag, rtol=1e-5)
