#!/usr/bin/python
# -*- coding: utf-8 -*-

from jitcode import jitcode, provide_basic_symbols
import numpy as np
import sympy


# generate adjacency matrix of one-dimensional small-world
# --------------------------------------------------------

# network parameters
n = 30	# number of nodes
m = 3	# number of nearest neighbours on each side
p = 0.1	# rewiring probability

# lattice
A = np.zeros( (n,n), dtype=int )
for i in range(n):
	for j in range(-m,m+1):
		A[i,(i+j)%n] = 1

# rewiring
for i in range(n):
	for j in range(j):
		if A[i,j] and (np.random.random() < p):
			A[j,i] = A[i,j] = 0
			while True:
				i_new,j_new = np.random.randint(0,n,2)
				if A[i_new,j_new] or i_new==j_new:
					continue
				else:
					A[j_new,i_new] = A[i_new,j_new] = 1
					break


# generate differential equations
# -------------------------------

t, y = provide_basic_symbols()

# control parameters
omega = np.random.uniform(0.8,1.0,n)
a = 0.165
b = 0.2
c = 10.0
coupling_strength = 0.1

# twenty Rösslers; first all x, then all y, finally all z.
f  = [ -omega[i] * y(i+n) - y(i+2*n) for i in range(n) ]
f += [ omega[i] * y(i) + a*y(i+n) for i in range(n) ]
f += [ b + y(i+2*n) * (y(i) - c) for i in range(n) ]

# diffusive coupling of the first component
for i in range(n):
	f[i] += sympy.Mul(
		coupling_strength,
		sum( A[i,j] * (y(j)-y(i)) for j in range(n) ),
		evaluate = False
		)
	#f[i] += coupling_strength * sum( A[i,j] * (y(j)-y(i)) for j in range(n) )



# integrate
# ---------

initial_state = np.random.random(3*n)

ODE = jitcode(f)
ODE.generate_f_C(simplify=False, do_cse=False)
ODE.set_integrator('dopri5')
ODE.set_initial_value(initial_state,0.0)

data = np.vstack(ODE.integrate(T) for T in range(10,100000,10))

# data structure: x[0], …, x[20], y[0], …, y[20], z[0], …, z[20]
np.savetxt("twenty_Rösslers.dat", data)
