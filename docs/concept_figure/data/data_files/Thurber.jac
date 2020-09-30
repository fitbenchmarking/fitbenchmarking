# Jacobian for NIST problem Thurber
# Computed using Mathematica workbook in
# fitbenchmarking/jacobian/scripts/NIST-Jacobians.nb

J = {(1 + b5*x + b6*x**2 + b7*x**3)**(-1),
    x/(1 + b5*x + b6*x**2 + b7*x**3), 
    x**2/(1 + b5*x + b6*x**2 + b7*x**3),
    x**3/(1 + b5*x + b6*x**2 + b7*x**3), 
    -((x*(b1 + b2*x + b3*x**2 + b4*x**3))/(1 + b5*x + b6*x**2 + b7*x**3)**2), 
    -((x**2*(b1 + b2*x + b3*x**2 + b4*x**3))/(1 + b5*x + b6*x**2 + b7*x**3)**2), 
    -((x**3*(b1 + b2*x + b3*x**2 + b4*x**3))/(1 + b5*x + b6*x**2 + b7*x**3)**2)}