#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from jitcode import jitcode, provide_basic_symbols
import numpy as np
import sympy


# generate adjacency matrix of two-dimensional small-world
# --------------------------------------------------------

# network parameters
s = 100 	# number of nodes in one direction
n = s*s
m = 60  	# number of nearest neighbours on each side
p = 0.18	# rewiring probability

# lattice
def squared_distance_from_origin(point):
	i,j = point
	return min(i,abs(s-i))**2 + min(j,abs(s-j))**2

neighbour_offsets = sorted(
	((i,j) for i in range(s) for j in range(s) if (i,j)!=(0,0)),
	key = squared_distance_from_origin
	)[:m]

def edges():
	for i in range(s):
		for j in range(s):
			for a,b in neighbour_offsets:
				k = (i+a)%s
				l = (j+b)%s
				x = i*s+j
				y = k*s+l
				if x < y:
					yield (x,y)

print("created lattice")

# rewire and write to adjacency matrix
A = np.zeros( (n,n), dtype=bool )
for edge in edges():
	if (np.random.random() < p) or A[edge]:
		while True:
			edge = tuple(np.random.randint(0,n,2))
			if (not A[edge]) and edge[0]!=edge[1]:
				break
	A[edge] = True
	A[edge[::-1]] = True

assert(np.all(A==A.T))
assert(not np.any(np.diag(A)))
assert(np.sum(A)/n == 60)

print("rewired")

# generate differential equations
# -------------------------------

t, y = provide_basic_symbols()

# control parameters
a = -0.0276
b = lambda: np.random.uniform(0.006, 0.014)
c =  0.02
coupling = 0.128/m

# The FitzHughs:
def f():
	for i in range(n):
		if (i%100==0): print(i)
		
		dx = y(i) * ( a-y(i) ) * ( y(i)-1.0 ) - y(i+n)
		dx += sympy.Mul(
			coupling,
			sum( y(j)-y(i) for j in range(n) if A[i,j] ),
			evaluate = False
			)
		yield dx
	
	for i in range(n):
		if (i%100==0): print(i)
		yield b()*y(i) - c*y(i+n)

print("created differential equations")

# integrate
# ---------

initial_state = np.random.random(2*n)

ODE = jitcode(f, n=2*n)
print(ODE._tmpfile())
ODE.generate_f_C(simplify=False, do_cse=False, chunk_size=100)
print("generated C code")
ODE.compile_C(
	extra_compile_args = [
		'-O0',
		'-march=native',
		'-mtune=native',
		'-Wno-unknown-pragmas',
		'-ffast-math'
		],
	verbose=True
	)
print("compiled C code")
ODE.set_integrator('dopri5')
ODE.set_initial_value(initial_state,0.0)

ausgabe = open("timeseries.dat", "w")
for T in range(100000):
	if (T%100==0):
		print(T)
	state = ODE.integrate(T)
	x_average = np.average(state[:n])
	y_average = np.average(state[n:])
	ausgabe.write("%f\t%f\n" % (x_average, y_average))
