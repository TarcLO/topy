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

from sympy import symbols, Matrix, diff, integrate, zeros, eye
from numpy import abs, array

from ..utils import get_logger

logger = get_logger(__name__)

def create_K(_L, _E, _nu, _k):
    # Initialize variables
    _a, _b, _c = _L, _L, _L  # element dimensions (half-lengths)
    _G = _E / (2 * (1 + _nu))  # modulus of rigidity
    _g = _E /  ((1 + _nu) * (1 - 2 * _nu))

    # SymPy symbols:
    a, b, x, y = symbols('a b x y')
    E, nu = symbols('E nu')
    N1, N2, N3, N4 = symbols('N1 N2 N3 N4')
    xlist = [x, x, x, x, x, x, x, x]
    ylist = [y, y, y, y, y, y, y, y]
    yxlist = [y, x, y, x, y, x, y, x]

    # Shape functions:
    N1 = (a - x) * (b - y) / (4 * a * b)
    N2 = (a + x) * (b - y) / (4 * a * b)
    N3 = (a + x) * (b + y) / (4 * a * b)
    N4 = (a - x) * (b + y) / (4 * a * b)

    # Create strain-displacement matrix B:
    B0 = tuple(map(diff, [N1, 0, N2, 0, N3, 0, N4, 0], xlist))
    B1 = tuple(map(diff, [0, N1, 0, N2, 0, N3, 0, N4], ylist))
    B2 = tuple(map(diff, [N1, N1, N2, N2, N3, N3, N4, N4], yxlist))
    B = Matrix([B0, B1, B2])

    # Create constitutive (material property) matrix for plane stress:
    C = (E / (1 - nu**2)) * Matrix([[1, nu, 0],
                                    [nu, 1, 0],
                                    [0,  0, (1 - nu) / 2]])

    PI = eye(3)
    PH2 = Matrix([[y / b, 0], [0, x / a], [0, 0]])
    P = PI.row_join(PH2)
    tP = P.transpose()

    dJ = tP * B
    dH = tP * C.inv() * P

    # Integration:
    logger.info('SymPy is integrating: K for Q5B...')
    J = dJ.integrate((x, -a, a),(y, -b, b))
    H = dH.integrate((x, -a, a),(y, -b, b))

    # Convert SymPy Matrix to NumPy array:
    K = J.transpose() * H.inv() * J

    # Convert SymPy Matrix to NumPy array:
    K = array(K.subs({a:_a, b:_b, E:_E, nu:_nu})).astype('double')

    # Set small (<< 0) values equal to zero:
    K[abs(K) < 1e-6] = 0

    # Return result:
    logger.info('Created stiffness matrix.')
    return K

# EOF Q5B_K.py
