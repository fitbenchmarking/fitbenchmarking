# Jacobian for NIST problem Eckerle4
# Computed using Mathematica workbook in
# fitbenchmarking/jacobian/scripts/NIST-Jacobians.nb

J = {1/(b2*exp((0.5*(-b3 + x)**2)/b2**2)), 
    -(b1/(b2**2*exp((0.5*(-b3 + x)**2)/b2**2))) +
    (1.*b1*(-b3 + x)**2)/(b2**4*exp((0.5*(-b3 + x)**2)/b2**2)),
    (1.*b1*(-b3 + x))/(b2**3*exp((0.5*(-b3 + x)**2)/b2**2))}