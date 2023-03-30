# Jacobian for NIST problem Bennett5
# Computed using Mathematica workbook in
# fitbenchmarking/jacobian/scripts/NIST-Jacobians.nb

J = {(b2 + x)**(-b3**(-1)),
    -((b1*(b2 + x)**(-1 - b3**(-1)))/b3), 
    (b1*Log[b2 + x])/(b3**2*(b2 + x)**b3**(-1))}