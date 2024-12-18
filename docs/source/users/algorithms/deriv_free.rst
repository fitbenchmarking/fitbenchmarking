.. _deriv_free:

****************
Derivative Free
****************

Derivative Free methods do not compute the gradient of a function and so are often used to minimize problems with
nondifferentiable functions. Some derivative free methods will attempt to approximate the gradient using a finite difference
approach, another class of methods constructs a linear or quadratic model of the objective functions and uses a trust
region approach to find the next iterate. Another widely used derivative free method is the Nelder-Mead simplex method. [Nocedal]_

To select all minimizers in fitbenchmarking that use derivative free methods, use the algorithm type ``deriv_free``.

.. _simplex:

Simplex (``simplex``)
*********************
Nelder-Mead is a simplex based algorithm, with a simplex :math:`S` in :math:`{\rm I\!R}` being defined as the convex hull of :math:`n+1` vertices :math:`\{x_1, ..., x_{n+1}\}`.

In an iteration of the algorithm, the idea is to remove the vertex with the worst function value. It is then replaced with another point with a better value. An iteration consists of the following steps:

1. **Ordering** the vertices of :math:`S` so that :math:`f(x_1) \leq f(x_2) \leq ... \leq f(x_{n+1})`

2. Calculating the **centroid**, :math:`\bar{x}` of the best :math:`n` points :math:`\bar{x} = \frac{1}{n} \sum_{i=1}^n x_i`

3. Carry out a **transformation** to compute the new simplex. Try to replace only the worst vertex :math:`x_{n+1}` with a better point, which then becomes the new vertex. If this fails, the simplex is shrunk towards the best vertex :math:`x_1` and :math:`n` new vertices are computed.
   The algorithm terminates when the simplex :math:`S` is sufficiently small. [Singer]_

**Advantages**: 
    - Method only requires 1 or 2 functions evaluations per iteration.
    - Gives significant improvements in first few iterations - quick to produce satisfactory results.

**Disadvantages**:
    - Stagnation can occur at non-optimal points, with large numbers of iterations leading to negligible improvement even when nowhere near a minimum.
    - If numerical computation of function derivative can be trusted, then other algorithms are more robust.

[Singer]_

.. [Nocedal] Jorge Nocedal, Stephen J. Wright (2006), Numerical Optimization

.. [Singer] Saša Singer, John Nelder (2009) Nelder-Mead algorithm. Scholarpedia, 4(7):2928.
