# Jacobian for NIST problem MGH10
# Computed using Mathematica workbook in
# fitbenchmarking/jacobian/scripts/NIST-Jacobians.nb

J = {exp(b2/(b3 + x)),
    (b1*exp(b2/(b3 + x)))/(b3 + x), 
    -((b1*b2*exp(b2/(b3 + x)))/(b3 + x)**2)}
