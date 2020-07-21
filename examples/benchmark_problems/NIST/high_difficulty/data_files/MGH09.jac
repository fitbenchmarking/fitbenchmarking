# Jacobian for NIST problem MGH09
# Computed using Mathematica workbook in
# fitbenchmarking/jacobian/scripts/NIST-Jacobians.nb

J = {(b2*x + x**2)/(b4 + b3*x + x**2),
    (b1*x)/(b4 + b3*x + x**2), 
    -((b1*x*(b2*x + x**2))/(b4 + b3*x + x**2)**2), 
    -((b1*(b2*x + x**2))/(b4 + b3*x + x**2)**2)}