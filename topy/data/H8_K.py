﻿"""
# =============================================================================
# Creates the stiffness matrix as requested, using the material properties 
# provided in the TPD file (for v2020 files).
#
# Author: William Hunter, Tarcísio L. de Oliveira
# Copyright (C) 2008, 2015, William Hunter.
# Copyright (C) 2020, Tarcísio L. de Oliveira
# =============================================================================
"""
from __future__ import division

import os

from sympy import symbols, Matrix, diff, integrate, zeros, lambdify
from numpy import array, sqrt, abs
from scipy.integrate import tplquad
import multiprocessing
from multiprocessing.pool import ThreadPool

from ..utils import get_logger

logger = get_logger(__name__)

def create_K(_L, _E, _nu, _k, _t):
    # Initialize variables
    _a, _b, _c = _L, _L, _L  # element dimensions (half-lengths)
    _G = _E / (2 * (1 + _nu))  # modulus of rigidity
    _g = _E /  ((1 + _nu) * (1 - 2 * _nu))

    # SymPy symbols:
    x, y, z = symbols('x y z')
    N1, N2, N3, N4 = symbols('N1 N2 N3 N4')
    N5, N6, N7, N8 = symbols('N5 N6 N7 N8')
    o = symbols('o') #  dummy symbol
    xlist = [x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x]
    ylist = [y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y, y]
    zlist = [z, z, z, z, z, z, z, z, z, z, z, z, z, z, z, z, z, z, z, z, z, z, z, z]
    yxlist = [y, x, o, y, x, o, y, x, o, y, x, o, y, x, o, y, x, o, y, x, o, y, x, o]
    zylist = [o, z, y, o, z, y, o, z, y, o, z, y, o, z, y, o, z, y, o, z, y, o, z, y]
    zxlist = [z, o, x, z, o, x, z, o, x, z, o, x, z, o, x, z, o, x, z, o, x, z, o, x]

    # Shape functions:
    N1 = (_a - x) * (_b - y) * (_c - z) / (8 * _a * _b * _c)
    N2 = (_a + x) * (_b - y) * (_c - z) / (8 * _a * _b * _c)
    N3 = (_a + x) * (_b + y) * (_c - z) / (8 * _a * _b * _c)
    N4 = (_a - x) * (_b + y) * (_c - z) / (8 * _a * _b * _c)
    N5 = (_a - x) * (_b - y) * (_c + z) / (8 * _a * _b * _c)
    N6 = (_a + x) * (_b - y) * (_c + z) / (8 * _a * _b * _c)
    N7 = (_a + x) * (_b + y) * (_c + z) / (8 * _a * _b * _c)
    N8 = (_a - x) * (_b + y) * (_c + z) / (8 * _a * _b * _c)

    # Create strain-displacement matrix B:
    B0 = tuple(map(diff, [N1, 0, 0, N2, 0, 0, N3, 0, 0, N4, 0, 0,\
                    N5, 0, 0, N6, 0, 0, N7, 0, 0, N8, 0, 0], xlist))
    B1 = tuple(map(diff, [0, N1, 0, 0, N2, 0, 0, N3, 0, 0, N4, 0,\
                    0, N5, 0, 0, N6, 0, 0, N7, 0, 0, N8, 0], ylist))
    B2 = tuple(map(diff, [0, 0, N1, 0, 0, N2, 0, 0, N3, 0, 0, N4,\
                    0, 0, N5, 0, 0, N6, 0, 0, N7, 0, 0, N8], zlist))
    B3 = tuple(map(diff, [N1, N1, N1, N2, N2, N2, N3, N3, N3, N4, N4, N4,\
                    N5, N5, N5, N6, N6, N6, N7, N7, N7, N8, N8, N8], yxlist))
    B4 = tuple(map(diff, [N1, N1, N1, N2, N2, N2, N3, N3, N3, N4, N4, N4,\
                    N5, N5, N5, N6, N6, N6, N7, N7, N7, N8, N8, N8], zylist))
    B5 = tuple(map(diff, [N1, N1, N1, N2, N2, N2, N3, N3, N3, N4, N4, N4,\
                    N5, N5, N5, N6, N6, N6, N7, N7, N7, N8, N8, N8], zxlist))
    B = Matrix([B0, B1, B2, B3, B4, B5])

    # Create constitutive (material property) matrix:
    C = Matrix([[(1 - _nu) * _g, _nu * _g, _nu * _g, 0, 0, 0],
                [_nu * _g, (1 - _nu) * _g, _nu * _g, 0, 0, 0],
                [_nu * _g, _nu * _g, (1 - _nu) * _g, 0, 0, 0],
                [0, 0, 0,                           _G, 0, 0],
                [0, 0, 0,                           0, _G, 0],
                [0, 0, 0,                           0, 0, _G]])

    dK = B.T * C * B

    logger.info('SymPy is integrating: K for H8...')
    p = ThreadPool(int(multiprocessing.cpu_count()))
    dK_create = lambda k: lambdify((x, y, z), k, "numpy")
    dK = p.map(dK_create, dK)

    # Integration:
    dK_integrate = lambda k: tplquad(k, -_a, _a, lambda x: -_b, lambda x: _b, lambda x, y: -_c, lambda x, y: _c)[0]
    K = array(p.map(dK_integrate, dK)).reshape(int(sqrt(len(dK))), -1)
    K = K.astype('double')

    C = array(C, dtype='double')

    # Set small (<< 0) values equal to zero:
    K[abs(K) < 1e-6] = 0

    # Return result:
    logger.info('Created stiffness matrix.')
    return K, B, C

# EOF H8_K.py
