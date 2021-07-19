from sympy import symbols, hessian, Matrix
from sympy.functions import exp


def gradient(f, v): return Matrix([f]).jacobian(v)


x, b1, b2, b3, b4, b5, b6, b7, b8 = symbols('x,b1,b2,b3,b4,b5,b6,b7,b8')

print('NIST Low Difficulty')
print('\nChwirut')
print('y = exp(-b1*x)/(b2+b3*x)  +  e')

r = exp(-b1*x)/(b2+b3*x)
v = [b1, b2, b3]

print('Jacobian:')
print(gradient(r, v))

print('Hessian:')
print(hessian(r, v))

print('\nChwirut2')
print('y = exp(-b1*x)/(b2+b3*x)  +  e')

r = exp(-b1*x)/(b2+b3*x)
v = [b1, b2, b3]

print('Jacobian:')
print(gradient(r, v))

print('Hessian:')
print(hessian(r, v))

print('\nDanWood')
print('y  = b1*x**b2  +  e')

r = b1*x**b2
v = [b1, b2]

print('Jacobian:')
print(gradient(r, v))

print('Hessian:')
print(hessian(r, v))

print('\nGauss1')
print('y = b1*exp( -b2*x ) + b3*exp( -(x-b4)**2 / b5**2) '
      '+ b6*exp( -(x-b7)**2 / b8**2 ) + e')

r = b1*exp(-b2*x) + b3*exp(-(x-b4)**2 / b5**2) + b6*exp(-(x-b7)**2 / b8**2)
v = [b1, b2, b3, b4, b5, b6, b7, b8]

print('Jacobian:')
print(gradient(r, v))

print('Hessian:')
print(hessian(r, v))

print('\nGauss2')
print('y = b1*exp( -b2*x ) + b3*exp( -(x-b4)**2 / b5**2) '
      '+ b6*exp( -(x-b7)**2 / b8**2 ) + e')

r = b1*exp(-b2*x) + b3*exp(-(x-b4)**2 / b5**2) + b6*exp(-(x-b7)**2 / b8**2)
v = [b1, b2, b3, b4, b5, b6, b7, b8]

print('Jacobian:')
print(gradient(r, v))

print('Hessian:')
print(hessian(r, v))

print('\nLanczos3')
print('y = b1*exp(-b2*x) + b3*exp(-b4*x) + b5*exp(-b6*x)  +  e')

r = b1*exp(-b2*x) + b3*exp(-b4*x) + b5*exp(-b6*x)
v = [b1, b2, b3, b4, b5, b6]

print('Jacobian:')
print(gradient(r, v))

print('Hessian:')
print(hessian(r, v))

print('\nMisra1a')
print('y = b1*(1-exp(-b2*x))  +  e')

r = b1*(1-exp(-b2*x))
v = [b1, b2]

print('Jacobian:')
print(gradient(r, v))

print('Hessian:')
print(hessian(r, v))

print('\nMisra1b')
print('y = b1 * (1-(1+b2*x/2)**(-2))  +  e')

r = b1 * (1-(1+b2*x/2)**(-2))
v = [b1, b2]

print('Jacobian:')
print(gradient(r, v))

print('Hessian:')
print(hessian(r, v))
