# Jacobian for NIST problem MGH17
# Computed using Mathematica workbook in
# fitbenchmarking/jacobian/scripts/NIST-Jacobians.nb

J = {1,
    exp(-(b4*x)),
    exp(-(b5*x)),
    -((b2*x)/exp(b4*x)),
    -((b3*x)/exp(b5*x))}