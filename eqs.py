#!/usr/bin/env python3

from sympy import symbols, Eq, latex
from sympy.vector import CoordSys3D
from sympy import diff
import os

# Initialize symbols
F, m, a, W, KE, k, q1, q2, r, mu_0, I, epsilon_0, Phi_E, t, P, V, n, R, T = symbols(
    'F m a W KE k q1 q2 r mu_0 I epsilon_0 Phi_E t P V n R T'
)

N = CoordSys3D('N')

# Equations
eq_newton = Eq(F, m * a)
eq_work_energy = Eq(W, KE)
eq_coulomb = Eq(F, k * q1 * q2 / r ** 2)
eq_ampere = Eq(F, mu_0 * (I + epsilon_0 * diff(Phi_E, t)))
eq_ideal_gas = Eq(P * V, n * R * T)

equations = [eq_newton, eq_work_energy, eq_coulomb, eq_ampere, eq_ideal_gas]

# Create LaTeX document
latex_code = "\\documentclass{article}\n\\usepackage{amsmath}\n\\begin{document}\n"
for eq in equations:
    latex_code += "\\[" + latex(eq) + "\\]\n"
latex_code += "\\end{document}"

# Save to .tex file
with open("equations.tex", "w") as f:
    f.write(latex_code)

# Generate PDF using pdflatex
os.system("pdflatex equations.tex")

