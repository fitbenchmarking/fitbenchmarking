.. _trust_region:

*************
Trust Region
*************

Trust region approach involves constructing a model function :math:`m_k` that approximates the function :math:`f` in the region, :math:`\Delta`, near the current point :math:`x_k`. 
The model :math:`m_k` is often a quadratic obtained by a Taylor Series expansion of the function around :math:`x_k`.

.. math::
    m_k(p) = f_k + \nabla f(x_k)^T p + \frac{1}{2} p^T B_k p

where :math:`B_k` is an approximation of the Hessian.

The subproblem to be solved at each iteration in order to find the step length is :math:`\min_p m_k(p)`, subject to :math:`\|p\| \leq \Delta_k`. [Nocedal]_

To select all minimizers in fitbenchmarking that use a trust region approach, use the algorithm type ``trust_region``.

.. _levenberg_marquardt:

Levenberg-Marquardt (``levenberg-Marquardt``)
*********************************************
Most widely used optimization algorithm, which uses the same Hessian approximation as Gauss-Newton but uses a trust region strategy instead of line search. As the Hessian approximation is the same as Gauss-Newton, convergence rate is similar.

For Levenberg-Marquardt, the model function :math:`m_k`, is chosen to be

.. math::
    m_k(p) = \frac{1}{2} \|r_k\|^2 + p^T J_k^T r_k + \frac{1}{2} p^T J_k^T J_k p

So, for a spherical trust region, the subproblem to be solved at each iteration is :math:`\min_p \frac{1}{2} \|J_k p + r_k\|^2`, subject to :math:`\|p\| \leq \Delta_k`.

Levenberg-Marquardt uses a combination of gradient descent and Gauss-Newton method. When the solution :math:`p^{GN}` lies inside of the trust region :math:`\Delta`, then :math:`p^{GN}` also solves the sub-problem. Otherwise, the current iteration is far from the optimal value and so the search direction is determined using steepest descent, which performs better than Gauss-Newton when far from the minimum.

**Advantages**:
    - Robust (more so than Gauss-Newton).
    - Avoids the weakness with Gauss-Newton that Jacobian must be full rank.
    - Fast to converge.
    - Good initial guess not required.

**Disadvantages**:
    - Similarly to Gauss-Newton, not good for large residual problems.
    - Can be slow to converge if a problem has many parameters

[Nocedal]_ [Ranganathan]_

.. [Nocedal] Jorge Nocedal, Stephen J. Wright (2006), Numerical Optimization

.. [Ranganathan] Ananth Ranganathan (2004), The Levenberg-Marquardt Algorithm, University of California, Santa Barbara
