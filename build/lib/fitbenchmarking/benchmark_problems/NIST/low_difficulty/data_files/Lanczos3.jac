# Jacobian for NIST problem Lanczos3
# Computed using Mathematica workbook in
# fitbenchmarking/jacobian/scripts/NIST-Jacobians.nb

J = {exp(-(b2*x)),
     -((b1*x)/exp(b2*x)),
     exp(-(b4*x)),
     -((b3*x)/exp(b4*x)), 
     exp(-(b6*x)),
     -((b5*x)/exp(b6*x))}