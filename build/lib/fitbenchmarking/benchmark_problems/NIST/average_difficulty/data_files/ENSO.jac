# Jacobian for NIST problem ENSO
# Computed using Mathematica workbook in
# fitbenchmarking/jacobian/scripts/NIST-Jacobians.nb

J = {1,
     cos((2*pi*x)/12),
     sin[(2*pi*x)/12],
     (-2*b6*pi*x*cos[(2*pi*x)/b4])/b4**2 + (2*b5*pi*x*sin[(2*pi*x)/b4])/b4**2,
     cos[(2*pi*x)/b4],
     sin[(2*pi*x)/b4], 
     (-2*b9*pi*x*cos[(2*pi*x)/b7])/b7**2 + (2*b8*pi*x*sin[(2*pi*x)/b7])/b7**2, 
     cos[(2*pi*x)/b7],
     sin[(2*pi*x)/b7]}