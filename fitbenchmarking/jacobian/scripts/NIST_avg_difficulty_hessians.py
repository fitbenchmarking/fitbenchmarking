from sympy import symbols, hessian, pi, Matrix
from sympy.functions import exp, cos, sin


def gradient(f, v): return Matrix([f]).jacobian(v)


x, b1, b2, b3, b4, b5, b6, b7, b8, b9 = symbols('x,b1,b2,b3,b4,b5,b6,b7,b8,b9')

print('NIST Average Difficulty')
print('\nENSO')
print('y = b1 + b2*cos( 2*pi*x/12 ) + b3*sin( 2*pi*x/12 )'
      '+ b5*cos( 2*pi*x/b4 ) + b6*sin( 2*pi*x/b4 )'
      '+ b8*cos( 2*pi*x/b7 ) + b9*sin( 2*pi*x/b7 )  + e')

r = b1 + b2*cos(2*pi*x/12) + b3*sin(2*pi*x/12) + b5*cos(2*pi*x/b4) + \
    b6*sin(2*pi*x/b4) + b8*cos(2*pi*x/b7) + b9*sin(2*pi*x/b7)
v = [b1, b2, b3, b4, b5, b6, b7, b8, b9]

print('Jacobian:')
print(gradient(r, v))

print('Hessian:')
print(hessian(r, v))

print('\nGauss3')
print('y = b1*exp( -b2*x ) + b3*exp( -(x-b4)**2 / '
      'b5**2 ) + b6*exp( -(x-b7)**2 / b8**2 ) + e')

r = b1*exp(-b2*x) + b3*exp(-(x-b4)**2 / b5**2) + b6*exp(-(x-b7)**2 / b8**2)
v = [b1, b2, b3, b4, b5, b6, b7, b8]

print('Jacobian:')
print(gradient(r, v))

print('Hessian:')
print(hessian(r, v))

print('\nHahn1')
print('y = (b1+b2*x+b3*x**2+b4*x**3)/(1+b5*x+b6*x**2+b7*x**3) + e')

r = (b1+b2*x+b3*x**2+b4*x**3)/(1+b5*x+b6*x**2+b7*x**3)
v = [b1, b2, b3, b4, b5, b6, b7]

print('Jacobian:')
print(gradient(r, v))

print('Hessian:')
print(hessian(r, v))

print('\nKirby2')
print('y = (b1 + b2*x + b3*x**2)/(1 + b4*x + b5*x**2)  +  e')

r = (b1 + b2*x + b3*x**2)/(1 + b4*x + b5*x**2)
v = [b1, b2, b3, b4, b5]

print('Jacobian:')
print(gradient(r, v))

print('Hessian:')
print(hessian(r, v))

print('\nLanczos1')
print('b1*exp(-b2*x) + b3*exp(-b4*x) + b5*exp(-b6*x)  +  e')

r = b1*exp(-b2*x) + b3*exp(-b4*x) + b5*exp(-b6*x)
v = [b1, b2, b3, b4, b5, b6]

print('Jacobian:')
print(gradient(r, v))

print('Hessian:')
print(hessian(r, v))

print('\nLanczos2')
print('y = b1*exp(-b2*x) + b3*exp(-b4*x) + b5*exp(-b6*x)  +  e')

r = b1*exp(-b2*x) + b3*exp(-b4*x) + b5*exp(-b6*x)
v = [b1, b2, b3, b4, b5, b6]

print('Jacobian:')
print(gradient(r, v))

print('Hessian:')
print(hessian(r, v))

print('\nMGH17')
print('y = b1 + b2*exp(-x*b4) + b3*exp(-x*b5)  +  e')

r = b1 + b2*exp(-x*b4) + b3*exp(-x*b5)
v = [b1, b2, b3, b4, b5]

print('Jacobian:')
print(gradient(r, v))

print('Hessian:')
print(hessian(r, v))

print('\nMisra1c')
print('y = b1 * (1-(1+2*b2*x)**(-.5))  +  e')

r = b1 * (1-(1+2*b2*x)**(-.5))
v = [b1, b2]

print('Jacobian:')
print(gradient(r, v))

print('Hessian:')
print(hessian(r, v))

print('\nMisra1d')
print('y = b1*b2*x*((1+b2*x)**(-1))  +  e')

r = b1*b2*x*((1+b2*x)**(-1))
v = [b1, b2]

print('Jacobian:')
print(gradient(r, v))

print('Hessian:')
print(hessian(r, v))
