# 2_Body_Problem.py

from math import sqrt
import matplotlib.pyplot as plt
import operator
from functools import reduce
from itertools import cycle


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

    def __mul__(self, other):
        if type(other) is self.__class__:
            raise NotImplementedError("Vector multiplication isn't implemented")
        else:
            return self.elementwise(lambda x: x * other)

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

    a = a_nd(R, G, m, i)
    v_i_new = Vector(*[new_v(component) for component in range(len(v_i[0]))])
    r_new = Vector(*[new_r(component) for component in range(len(R[0][0]))])
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

    a = a_nd(R, G, m, i)
    r_new = Vector(*[new_r(component) for component in range(len(R[0][0]))])
    v_i_new = Vector(*[new_v(component) for component in range(len(v_i[0]))])
    return v_i_new, r_new


def rk4 (delta_t, i, v_i, R, m, G):
    """ Forth-order Runge Kutta method """

    def a_rk(R, G, m, i, weight, r_tilde):
        """ Special acceleration for Runge Kutta method """
        a_new = []
        for j in range(len(R)):
            if i == j: continue
            r_i = R[i][-1]
            r_j = R[j][-1] 
            r_ij = r_j - r_i
            r_ij[0] = r_ij[0] + weight * r_tilde[0]
            r_ij[1] = r_ij[1] + weight * r_tilde[1]

            a_i = r_ij.elementwise(lambda x_n: G * m[j] * x_n / r_ij.norm**3)
            a_new.append(a_i)
        a = reduce(lambda v1, v2: v1 + v2, a_new)
        return a

    def v_tilde1(component):
        return a_1[component] * delta_t

    def r_tilde1(component):
        return v_i[-1][component] * delta_t

    def v_tilde2(component):
        return a_2[component] * delta_t

    def r_tilde2(component):
        return (v_i[-1][component] + 0.5 * v_tilde1_new[component]) * delta_t

    def v_tilde3(component):
        return a_3[component] * delta_t

    def r_tilde3(component):
        return (v_i[-1][component] + 0.5 * v_tilde2_new[component]) * delta_t

    def v_tilde4(component):
        return a_4[component] * delta_t

    def r_tilde4(component):
        return (v_i[-1][component] + 0.5 * v_tilde3_new[component]) * delta_t

    def new_v(component):
        return v_i[-1][component] + 1/6 * v_tilde1_new[component] \
            + 1/3 * v_tilde2_new[component] \
            + 1/3 * v_tilde3_new[component] \
            + 1/6 * v_tilde4_new[component]

    def new_r(component):
        return R[i][-1][component] + 1/6 * r_tilde1_new[component] \
            + 1/3 * r_tilde2_new[component] \
            + 1/3 * r_tilde3_new[component] \
            + 1/6 * r_tilde4_new[component]


    a_1 = a_nd(R, G, m, i)
    v_tilde1_new = Vector(*[v_tilde1(component) for component in range(len(v_i[0]))])
    r_tilde1_new = Vector(*[r_tilde1(component) for component in range(len(v_i[0]))])

    a_2 = a_rk(R, G, m, i, 0.5, r_tilde1_new)
    v_tilde2_new = Vector(*[v_tilde2(component) for component in range(len(v_i[0]))])
    r_tilde2_new = Vector(*[r_tilde2(component) for component in range(len(v_i[0]))])

    a_3 = a_rk(R, G, m, i, 0.5, r_tilde2_new)
    v_tilde3_new = Vector(*[v_tilde3(component) for component in range(len(v_i[0]))])
    r_tilde3_new = Vector(*[r_tilde3(component) for component in range(len(v_i[0]))])

    a_4 = a_rk(R, G, m, i, 1, r_tilde3_new)
    v_tilde4_new = Vector(*[v_tilde4(component) for component in range(len(v_i[0]))])
    r_tilde4_new = Vector(*[r_tilde4(component) for component in range(len(v_i[0]))])

    v_new = Vector(*[new_v(component) for component in range(len(v_i[0]))])
    r_new = Vector(*[new_r(component) for component in range(len(v_i[0]))])

    return v_new, r_new


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
n = 2

# Maximum integration time
t_max = 100.0

# Time step length
delta_t = 0.100

# Mass
m = [
    0.9999,
    0.00009]
M = sum(m)
# my = prod(m) / M # only for two body problem

# Initial position r and velocity v of the two bodys 
r1_start = Vector(0, 0)
v1_start = Vector(0, 0)
r2_start = Vector(1, 0)
v2_start = Vector(0, 1.4) 

r_start = [[r1_start], [r2_start]]
v_start = [[v1_start], [v2_start]]

# Gravity
G = 2.0

# 2 Calculation
# -------------
R = r_start
V = v_start

# Loop over time steps (start at 0, end at t_max, step = delta_t)
for t in range(0, int(t_max//delta_t)):
    for i in range(n):
        # v_i_new_e, r_i_new_e = euler(delta_t, i, V[i], R, m, G)
        # v_i_new_ec, r_i_new_ec = euler_cormer(delta_t, i, V[i], R, m, G)
        v_i_new_v, r_i_new_v = verlet(t, delta_t, i, V[i], R, m, G)
        v_i_new_rk, r_i_new_rk = rk4(delta_t, i, V[i], R, m, G)

        """
        print()
        print("Time = ", t, "Body = ", i)
        print("Euler vs Euler-Cormer: ", abs(r_i_new_e[0] - r_i_new_ec[0]))
        print("Euler vs Verlet: ", abs(r_i_new_e[0] - r_i_new[0]))
        print("Verlet vs RK: ", abs(r_i_new_v[0] - r_i_new_rk[0]))
        """
        # Choose with of the calculated values should be plotted
        r_i_new = r_i_new_rk
        v_i_new = v_i_new_rk
        
        R[i].append(r_i_new)
        V[i].append(v_i_new)


plt.axis([-1.5, 1.5, -1.5, 1.5])

colors = ["blue", "green"]

# adds the related color to each coordinate pair
a = (((coords, color) for (coords, color) in zip(body, cycle([color]))) for (body, color) in zip(R, cycle(colors)))
# zip coordinate pairs for each timestep together
b = iter(zip(*a))
previous_timestep = next(b)
for timestep in b:
    for body in zip(previous_timestep, timestep):
        (old_coords, _), (coords, body_color) = body
        plt.plot(*zip(old_coords, coords), color=body_color)
    plt.pause(0.0001)
    previous_timestep = timestep

plt.show()