# Jacobian for NIST problem Kirby2
# Computed using Mathematica workbook in
# fitbenchmarking/jacobian/scripts/NIST-Jacobians.nb

J = {(1 + b4*x + b5*x**2)**(-1),
    x/(1 + b4*x + b5*x**2), 
    x**2/(1 + b4*x + b5*x**2),
    -((x*(b1 + b2*x + b3*x**2))/(1 + b4*x + b5*x**2)**2),
    -((x**2*(b1 + b2*x + b3*x**2))/(1 + b4*x + b5*x**2)**2)}