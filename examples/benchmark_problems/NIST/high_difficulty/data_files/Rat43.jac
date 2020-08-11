# Jacobian for NIST problem RAT43
# Computed using Mathematica workbook in
# fitbenchmarking/jacobian/scripts/NIST-Jacobians.nb

J = {(1 + exp(b2 - b3*x))**(-b4**(-1)), 
    -((b1*exp(b2 - b3*x)*(1 + exp(b2 - b3*x))**(-1 - b4**(-1)))/b4), 
    (b1*exp(b2 - b3*x)*(1 + exp(b2 - b3*x))**(-1 - b4**(-1))*x)/b4, 
    (b1*Log[1 + exp(b2 - b3*x)])/(b4**2*(1 + exp(b2 - b3*x))**b4**(-1))}