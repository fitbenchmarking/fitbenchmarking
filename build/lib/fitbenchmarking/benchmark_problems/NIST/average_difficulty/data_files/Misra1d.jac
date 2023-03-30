# Jacobian for NIST problem Misra1d
# Computed using Mathematica workbook in
# fitbenchmarking/jacobian/scripts/NIST-Jacobians.nb

J = {(b2*x)/(1 + b2*x),
    -((b1*b2*x**2)/(1 + b2*x)**2) + (b1*x)/(1 + b2*x)}