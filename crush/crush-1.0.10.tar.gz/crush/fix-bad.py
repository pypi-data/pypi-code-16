import sys
import itertools
from abc import ABCMeta, abstractmethod

import numpy as np


def add_constraints(constraints):
    """Given a list of constraints combine them in a single one.
    
    A constraint is a function that accepts a selection and returns True
    if the selection is valid and False if not.
    """
    if constraints is None:
        return lambda s: True
    else:
        return lambda s: all(constraint(s) for constraint in constraints)


class BasePolicyFamily(metaclass=ABCMeta):    
    @abstractmethod
    def log_prob(self, s, params):
        """Compute the log probability of the selection 's' given the 
        parameters 'params'"""
        pass
    
    @abstractmethod
    def jac_log_prob(self, s, params):
        """Compute the jacobian of the log probability relative to the 
        parameters evaluated at the selection 's' and the parameters 'params'"""
        pass
    
    @abstractmethod
    def sample(self, params):
        """Extract just one random selection.
        
        The result should be a numpy array with as many elements as replicas.
        The i-th component represents the hard drive selected for the i-th replica.
        """
        pass

    @abstractmethod
    def params_point(self):
        """Give an example of valid parameters.
        
        This method is used as an starting point for optimization methods and testing.
        """
        pass
    
    def normalize_params(self, params):
        """Return new params making sure they fall betwenn valid bounds
        
        The new params should be as close as possible as the ones provided.
        For example it the parameters represent a probability distribution
        they should sum to 1.
        """
        return params
        
    def sample_constrained(self, params, size, constraints=None):
        samples = []
        g = add_constraints(constraints)
        while len(samples) < size:
            sample = self.sample(params)
            if g(sample):
                samples.append(sample)
        return np.stack(samples)
    
    def loss(self, params, constraints=None):
        g = add_constraints(constraints)
        z_g = 0
        z_u = np.zeros(len(self.c))
        jac_z_g = np.zeros_like(params)
        jac_z_u = np.zeros((len(self.c), len(params)))
        for s in itertools.permutations(np.arange(len(self.c)), self.R):
            if g(s):
                p = np.exp(self.log_prob(s, params))
                q = p*self.jac_log_prob(s, params)
                z_g += p
                jac_z_g += q
                for i in s:
                    z_u[i] += p
                    jac_z_u[i, :] += q
        L = (np.log(self.c) - np.log(z_u/z_g/self.R)) @ self.c
        J = -((jac_z_u.T/z_u).T - jac_z_g/z_g).T @ self.c
        return L, J
    
    def build_selector(self, params, constraints=None):
        """Builds a function accepting no arguments that returns a valid selection.
        
        A selection is represented by an array with as many components as hard drives.
        A zero entry means the hard drive is unused, otherwise it says what replica
        is stored there.
        """
        g = add_constraints(constraints)
        def selector():            
            sample = None
            while sample is None:
                candidate = self.sample(params)
                if g(candidate):
                    sample = candidate           
            return sample
        
        return selector

from crush import Crush
import random

class CrushPolicyFamily(BasePolicyFamily):
    def __init__(self, capacities, n_replicas):
        self.R = n_replicas
        self.c = np.array(capacities) / np.sum(capacities)
        self.init_crushmap()

    def init_crushmap(self):
        trees = [
            {"name": "dc1", "type": "root", "id": -1, 'children': []},
        ]
        trees[0]['children'].extend([
            {
                "type": "host",
                "id": -(i + 2),
                "name": "host%d" % i,
                "weight": self.c[i],
                "children": [
                    {"id": i,
                     "name": "device%02d" % (i), "weight": self.c[i]},
                ],
            } for i in range(len(self.c))
        ])
        crushmap = {
            "trees": trees,
            "rules": {
                "data": [
                    ["take", "dc1"],
                    ["chooseleaf", "firstn", 0, "type", "host"],
                    ["emit"]
                ]
            }
        }
        self.crush = Crush()
        self.crush.parse(crushmap)
        
    def params_point(self):
        return np.copy(self.c)
    
    def normalize_params(self, params):
        return params/np.sum(params)

    def log_prob(self, s, params):
        logP = 0
        for r in range(self.R):
            logP += np.log(params[s[r]])
            d = 1
            for i in range(r):                
                d -=  params[s[i]]
            logP -= np.log(d)
        return logP
    
    def jac_log_prob(self, s, params):
        jac = np.zeros_like(self.c)
        for r in range(self.R):
            jac[s[r]] += 1.0/params[s[r]]
            d = 1
            jac_d = np.zeros_like(self.c)
            for i in range(r):
                d -= params[s[i]]
                jac_d[s[i]] -= 1
            jac -= jac_d/d
        return jac
    
    def sample(self, params):
        s = self.crush.map(rule='data', value=random.randrange(100000), replication_count=self.R)
        s = np.copy(list(map(lambda n: self.crush.get_item_by_name(n)['id'], s)))
        return s

class SimplePolicyFamily(BasePolicyFamily):
    def __init__(self, capacities, n_replicas):
        self.c = np.array(capacities) / np.sum(capacities)
        self.R = n_replicas
        # Initialize the probability of choosing the first hard drive        
        L = self.c < 1/(self.R*len(self.c))
        M = np.logical_not(L)    
        self.p_1 = np.empty_like(self.c)
        self.p_1[L] = self.R*self.c[L]
        self.p_1[M] = 1/np.sum(M)*(1 - np.sum(self.p_1[L]))

    def params_point(self):
        return np.copy(self.p_1)
    
    def normalize_params(self, params):
        return params/np.sum(params)

    def log_prob(self, s, params):
        p_2 = params
        logP = np.log(self.p_1[s[0]])
        for r in range(1, self.R):
            logP += np.log(p_2[s[r]])
            d = 1
            for i in range(r):                
                d -=  p_2[s[i]]
            logP -= np.log(d)
        return logP
    
    def jac_log_prob(self, s, params):
        p_2 = params
        jac = np.zeros_like(self.c)
        for r in range(1, self.R):
            jac[s[r]] += 1.0/p_2[s[r]]
            d = 1
            jac_d = np.zeros_like(self.c)
            for i in range(r):
                d -= p_2[s[i]]
                jac_d[s[i]] -= 1
            jac -= jac_d/d
        return jac
    
    def sample(self, params):
        p_2 = params
        i = np.random.choice(len(self.p_1), p=self.p_1)
        selection = [i]
        p = np.copy(p_2)
        for r in range(1, self.R):
            p[i] = 0
            p /= np.sum(p)
            i = np.random.choice(len(p), p=p)
            selection.append(i)
        print('LLL ' + str(np.array(selection)))
        return np.array(selection)

def test_policy_jacobian(policy, params=None):
    if params is None:
        params = policy.params_point()
    sample = policy.sample(params)
    jac = np.zeros_like(params)
    dh = 1e-6
    for i in range(len(params)):
        params[i] += dh
        logP_1 = policy.log_prob(sample, params)
        params[i] -= 2*dh
        logP_2 = policy.log_prob(sample, params)
        params[i] += dh
        jac[i] = (logP_1 - logP_2)/(2*dh)
    assert(np.max(np.abs(jac - policy.jac_log_prob(sample, params))) < 1e-3)

policy = SimplePolicyFamily([10, 10, 5, 5, 4, 3, 0.01], 3)
test_policy_jacobian(policy)
policy = SimplePolicyFamily([10, 10, 5, 5, 4, 3], 3)
test_policy_jacobian(policy, np.array([0.3, 0.3, 0.1, 0.1, 0.1, 0.1]))
caps = 10*np.random.rand(6)
params = np.random.rand(6)
params /= np.sum(params)
policy = SimplePolicyFamily(caps, 2)
test_policy_jacobian(policy, params)

print(policy.sample_constrained(policy.params_point(), 5))

import warnings


def optimal_params(policy_family, start=None, 
                   constraints=None, step=1e-2, eps=1e-3, max_iter=500, verbose=0):
    """Apply gradient descent to find the optimal policy"""
    if start is None:
        start = policy_family.params_point()
    def loss(params):
        return policy_family.loss(params, constraints)
        
    params_old = np.copy(start)
    loss_old, jac_old = loss(params_old)
    it = 0
    while True:
#        print(str(params_old))
        params_new = policy_family.normalize_params(params_old - step*jac_old)        
        loss_new, jac_new = loss(params_new)
        jac_norm = np.sqrt(np.sum(jac_old**2))
        if loss_new > loss_old or jac_norm < eps:
            # converged
            break
        else:
            loss_old, jac_old = loss_new, jac_new
            params_old = params_new
            if it > max_iter:
                warnings.warn('max iter')
                break                                
        it += 1
        if verbose:
            print('it={0:>5d} jac norm={1:.2e} loss={2:.2e}'.format(it, jac_norm, loss_old))
    if verbose:
        print('Converged to desired accuracy :)')
    return params_old

def test_loss(policy, params):
    dh = 1e-6
    jac = np.empty_like(params)
    for i in range(len(params)):
        x = np.copy(params)
        x[i] += dh
        f1, j1 = policy.loss(x)
        x[i] -= 2*dh
        f2, j2 = policy.loss(x)
        jac[i] = (f1 - f2)/(2*dh)
    f0, j0 = policy.loss(params)
    assert(np.max(np.abs(jac - j0)) < 1e-3)

policy = SimplePolicyFamily([10, 8, 6, 6], 2)
test_loss(policy, policy.normalize_params(np.random.rand(4)))

policy = SimplePolicyFamily([10, 10, 10, 8, 8, 6, 6], 3)
optimal_params(policy, eps=1e-2, verbose=1)

def run_sim(N, selector, n=100000):
    results = np.zeros((n, N), dtype=int)
    for it in range(n):
        selected = selector()
        for r, i in enumerate(selected):
            results[it, i] = r + 1
    return results


def report(sim, expected, actual):
    print('Expected vs actual use ({0} samples)'.format(sim.shape[0]))
    for i in range(len(expected)):
        print(' disk {0}: {1:.2e} {2:.2e}'.format(i, expected[i], actual[i]))

cap = np.array([10, 8, 6, 10, 8, 6, 10, 8, 6])
#cap = np.array([10, 10, 10, 10, 1])

def constraint_1(s):
    """Never store the first replica on the biggest ones"""
    return cap[s[0]] != 10


def constraint_2(s):
    """Suppose that there are three groups:
    
             Hard drives
    Group 1: 1, 2, 3
    Group 2: 4, 5, 6
    Group 3: 7, 8, 9
    
    Don't store two replicas in the same group.
    """
    group = np.array([0, 0, 0, 1, 1, 1, 2, 2, 2])
    count = np.array([0, 0, 0])
    for i in s:
        count[group[i]] += 1
    return np.all(count <= 1)


for R in [2, 3]:
    for constraints in [None]:
        print('Simulation: R={0}, constraints: {1}'.format(R, constraints is not None))
        print(72*'-')
        pol = SimplePolicyFamily(cap, R)        
        opt = optimal_params(pol, constraints=constraints)
        sim = run_sim(len(cap), pol.build_selector(opt, constraints=constraints), n=4)
        print('KKKK ' + str(sim))
        print('First replica on each hard drive')
        report(sim, np.repeat(1/len(cap), len(cap)), np.mean(sim == 1, axis=0))
        print('All replicas on each hard drive')
        print('MMMM ' + str(sim > 0))
        report(sim, cap/np.sum(cap), 1/R*np.mean(sim > 0, axis=0))
        print('Sample:')
        print(sim[:10, :])
        print()
