# Jacobian for NIST problem Gauss3
# Computed using Mathematica workbook in
# fitbenchmarking/jacobian/scripts/NIST-Jacobians.nb

J = {exp(-(b2*x)),
    -((b1*x)/exp(b2*x)),
    exp(-((-b4 + x)**2/b5**2)), 
    (2*b3*(-b4 + x))/(b5**2*exp((-b4 + x)**2/b5**2)), 
    (2*b3*(-b4 + x)**2)/(b5**3*exp((-b4 + x)**2/b5**2)),
    exp(-((-b7 + x)**2/b8**2)), 
    (2*b6*(-b7 + x))/(b8**2*exp((-b7 + x)**2/b8**2)), 
    (2*b6*(-b7 + x)**2)/(b8**3*exp((-b7 + x)**2/b8**2))}