# Jacobian for NIST problem Chirwut2
# Computed using Mathematica workbook in
# fitbenchmarking/jacobian/scripts/NIST-Jacobians.nb


J = {-(x/(exp[b1*x]*(b2 + b3*x))),
     -(1/(exp[b1*x]*(b2 + b3*x)^2)), 
     -(x/(exp[b1*x]*(b2 + b3*x)^2))}