# Jacobian for NIST problem RAT42
# Computed using Mathematica workbook in
# fitbenchmarking/jacobian/scripts/NIST-Jacobians.nb

J = {(1 + exp(b2 - b3*x))**(-1),
    -((b1*exp(b2 - b3*x))/(1 + exp(b2 - b3*x))**2), 
    (b1*exp(b2 - b3*x)*x)/(1 + exp(b2 - b3*x))**2}