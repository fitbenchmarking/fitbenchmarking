from sympy import symbols, hessian, Matrix
from sympy.functions import exp


def gradient(f, v): return Matrix([f]).jacobian(v)


x, b1, b2, b3, b4, b5, b6, b7 = symbols('x,b1,b2,b3,b4,b5,b6,b7')

print('NIST Average Difficulty')
print('\nBennett5')
print('y = b1 * (b2+x)**(-1/b3)  +  e')

r = b1 * (b2+x)**(-1/b3)
v = [b1, b2, b3]

print('Jacobian:')
print(gradient(r, v))

print('Hessian:')
print(hessian(r, v))

print('\nBoxBOD')
print('b1*(1-exp(-b2*x))  +  e')

r = b1*(1-exp(-b2*x))
v = [b1, b2]

print('Jacobian:')
print(gradient(r, v))

print('Hessian:')
print(hessian(r, v))

print('\nEckerle4')
print('y = (b1/b2) * exp(-0.5*((x-b3)/b2)**2)  +  e')

r = (b1/b2) * exp(-0.5*((x-b3)/b2)**2)
v = [b1, b2, b3]

print('Jacobian:')
print(gradient(r, v))

print('Hessian:')
print(hessian(r, v))

print('\nMGH09')
print('y = b1*(x**2+x*b2) / (x**2+x*b3+b4)  +  e')

r = b1*(x**2+x*b2) / (x**2+x*b3+b4)
v = [b1, b2, b3, b4]

print('Jacobian:')
print(gradient(r, v))

print('Hessian:')
print(hessian(r, v))

print('\nMGH10')
print('y = b1 * exp(b2/(x+b3))  +  e')

r = b1 * exp(b2/(x+b3))
v = [b1, b2, b3]

print('Jacobian:')
print(gradient(r, v))

print('Hessian:')
print(hessian(r, v))

print('\nRat42')
print('y = b1 / (1+exp(b2-b3*x))  +  e')

r = b1 / (1+exp(b2-b3*x))
v = [b1, b2, b3]

print('Jacobian:')
print(gradient(r, v))

print('Hessian:')
print(hessian(r, v))

print('\nRat43')
print('y = b1 / ((1+exp(b2-b3*x))**(1/b4))  +  e')

r = b1 / ((1+exp(b2-b3*x))**(1/b4))
v = [b1, b2, b3, b4]

print('Jacobian:')
print(gradient(r, v))

print('Hessian:')
print(hessian(r, v))

print('\nThurber')
print('y = (b1 + b2*x + b3*x**2 + b4*x**3) / '
      '(1 + b5*x + b6*x**2 + b7*x**3)  +  e')

r = (b1 + b2*x + b3*x**2 + b4*x**3) / (1 + b5*x + b6*x**2 + b7*x**3)
v = [b1, b2, b3, b4, b5, b6, b7]

print('Jacobian:')
print(gradient(r, v))

print('Hessian:')
print(hessian(r, v))
