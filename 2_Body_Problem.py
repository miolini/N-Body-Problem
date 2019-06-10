# 2_Body_Problem.py

from math import sqrt
import matplotlib.pyplot as plt
import operator
from functools import reduce


class Vector():
    """ n-dimensional Vector """
    def __init__(self, *components):
        self._components = list(components)

    def __str__(self):
        return f"Vector{self._components}"

    __repr__ = __str__

    def two_vector_elementwise(self, other, func):
        if len(self) != len(other):
            raise ValueError("Dimensions of vectors are different")
        return Vector(*[func(s, o) for (s, o) in zip(self._components, other._components)])

    def elementwise(self, func):
        return Vector(*[func(x) for x in self._components])

    def __sub__(self, other):
        return self.two_vector_elementwise(other, operator.sub)

    def __add__(self, other):
        return self.two_vector_elementwise(other, operator.add)

    @property
    def norm(self):
        return sqrt(sum(x**2 for x in self._components))

    __abs__ = norm

    def __getitem__(self, index):
        return self._components[index]

    def __setitem__(self, index, value):
        self._components[index] = value

    def __len__(self):
        return len(self._components)

    dim = __len__



def euler (delta_t, i, v_i, R, m, G):
    """ Euler method to solve ODEs """
    def new_r(component):
        return R[i][-1][component] + v_i[-1][component] * delta_t

    def new_v(component): 
        return v_i[-1][component] + a[component] * delta_t

    a = a_nd(R, G, m, i)
    v_i_new = Vector(*[new_v(component) for component in range(len(v_i[0]))])
    r_new = Vector(*[new_r(component) for component in range(len(R[0][0]))])
    return v_i_new, r_new


def euler_cormer (delta_t, i, v_i, R, m, G):
    """ Euler-Cormer method to solve ODEs """
    def new_r(component):
        return R[i][-1][component] + 0.5 *  (v_i[-1][component] + v_i_new[component])* delta_t

    def new_v(component): 
        return v_i[-1][component] + a[component] * delta_t

    a = a_nd(R, G, m)
    v_i_new = [new_v(component) for component in range(len(v_i[0]))]
    r_new = [new_r(component) for component in range(len(R[0][0]))]
    return v_i_new, r_new


def verlet (t, delta_t, i, v_i, R, m, G):
    """ Verlet algorithm """
    def new_r(component):
        if t == 0:
            r_help = R[i][-1][component] - v_i[-1][component] * delta_t + a[component]/2 * delta_t**2
            return 2 * R[i][-1][component] - r_help + a[component] * delta_t**2
        else:
            return 2 * R[i][-1][component] - R[i][-2][component] + a[component] * delta_t**2

    def new_v(component):
        if t == 0:
            r_help = R[i][-1][component] - v_i[-1][component] * delta_t + a[component]/2 * delta_t**2
            return (r_new[component] - r_help) / (2 * delta_t)
        else:
            return (r_new[component] - R[i][-2][component]) / (2 * delta_t)

    a = a_nd(R, G, m)
    r_new = [new_r(component) for component in range(len(R[0][0]))]
    v_i_new = [new_v(component) for component in range(len(v_i[0]))]
    return v_i_new, r_new


def a_nd(R, G, m, i):
    """ Acceleration of next timestep for 1 body in a system of n bodies
    Acceleration as x and y components
    Params:
        R: Vector of vector of position tuples of elements
        G: Gravitational constant
        m: Vector of masses
    """
    a_new = []
    for j in range(len(R)):
        if i == j: continue
        r_i = R[i][-1]
        r_j = R[j][-1]
        r_ij = r_j - r_i

        a_i = r_ij.elementwise(lambda x_n: G * m[j] * x_n / r_ij.norm**3)
        a_new.append(a_i)
    a = reduce(lambda v1, v2: v1 + v2, a_new)
    return a


def prod(lst):
    return reduce(lambda a,b: a * b, lst)


# 1 Input Data
# ---------------
# Number of bodys
n = 3

# Maximum integration time
t_max = 220.0

# Time step length
delta_t = 0.10

# Mass
m = [
    0.9999, 
    0.00001, 
    0.00009]
M = sum(m)
# my = prod(m) / M # only for two body problem

# Initial position r and velocity v of the two bodys 
r1_start = Vector(0, 0)
v1_start = Vector(1, 0)
r2_start = Vector(-2.25, 0)
v2_start = Vector(0, 0)
r3_start = Vector(0, -1)
v3_start = Vector(0, 0.666666) 

r_start = [[r1_start], [r2_start], [r3_start]]
v_start = [[v1_start], [v2_start], [v3_start]]

# Gravity
G = 1.0

# 2 Calculation
# -------------
R = r_start
V = v_start

# Loop over time steps (start at 0, end at t_max, step = delta_t)
for t in range(0, int(t_max//delta_t)):
    print()
    for i in range(n):
        v_i_new_e, r_i_new_e = euler(delta_t, i, V[i], R, m, G)
        v_i_new_ec, r_i_new_ec = euler_cormer(delta_t, i, V[i], R, m, G)
        v_i_new, r_i_new = verlet(t, delta_t, i, V[i], R, m, G)

        print()
        print("Time = ", t, "Body = ", i)
        print("Euler vs Euler-Cormer: ", abs(r_i_new_e[0] - r_i_new_ec[0]))
        print("Euler vs Verlet: ", abs(r_i_new_e[0] - r_i_new[0]))
        
        R[i].append(r_i_new)
        V[i].append(v_i_new)


plt.axis([-20, 20, -20, 20])

for rs in zip(*R):
    for coords in rs:
        plt.scatter(*coords)
    plt.pause(0.0001)
"""
for n in range(n):
    plt.plot(*list(zip(*R[n])), "o", label=r"$R_{}$".format(n))
"""
plt.show()
