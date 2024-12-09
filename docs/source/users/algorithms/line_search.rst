.. _line_search:

*******************
Line Search Methods
*******************
In line search methods, each iteration is given by :math:`x_{k+1} = x_k + \alpha_k p_k`, where :math:`p_k` is the search direction and :math:`\alpha_k` is the step length.

The search direction is often of the form :math:`p_k = -B_k^{-1} \nabla f_k` where :math:`B_k` is a symmetric and non-singular matrix. The form of :math:`p_k` is dependent on algorithm choice.

The ideal step length would be :math:`min_{\alpha>0} f(x_k + \alpha p_k)` but this is generally too expensive to calculate. Instead an inexact line search condition such as the Wolfe Conditions can be used:

.. math::
    f(x_k + \alpha p_k) \leq f(x_k) + c_1 \alpha \nabla f_k^T p_k \\
    f(x_k + \alpha_k p_k)^T p_k \geq c_2 \nabla f_k^T p_k

With :math:`0<c_1<c_2<1`. Here, the first condition ensures that :math:`\alpha_k` gives a sufficient decrease in :math:`f`, whilst the second condition rules out unacceptably short steps. [Nocedal]_

.. _steepest_descent:

Steepest Descent (``steepest_descent``)
***************************************
Simple method where search direction :math:`p_k` is set to be :math:`-\nabla f_k`, i.e. the direction along which :math:`f` decreases most rapidly.

**Advantages**:
    - Low storage requirements
    - Easy to compute

**Disadvantages**:
    - Slow convergence for nonlinear problems

[Nocedal]_

.. _conjugate_gradient:

Conjugate Gradient (``conjugate_gradient``)
*******************************************
Conjugate Gradient methods have a faster convergence rate than Steepest Descent but avoid the high computational cost of methods where the inverse Hessian is calculated.

Given an iterate :math:`x_0`, evaluate :math:`f_0 = f(x_0), \nabla f_0 = \nabla f(x_0)`.

Set :math:`p_0 \leftarrow - \nabla f_0, k \leftarrow 0`

Then while :math:`\nabla f_k \neq 0`:

Carry out a line search to compute the next iterate, then evaluate :math:`\nabla f_{k+1}` and use this to determine the subsequent conjugate direction :math:`p_{k+1} = - \nabla f(x_{k+1}) + \beta_k p_k`

Different variations of the Conjugate Gradient algorithm use different formulas for :math:`\beta_k`, for example:

Fletcher-Reeves: :math:`\beta_{k+1} = \frac{f_{k+1}^T \nabla f_{k+1}}{\nabla f_k^T \nabla f_k}`
Polak-Ribiere:  :math:`\beta_{k+1} = \frac{ \nabla f_{k+1}^T ( \nabla f_{k+1} - \nabla f_k)}{\|\nabla f_k\|^2}`

[Nocedal]_ [Poczos]_

**Advantages**:
    - Considered to be one of the best general purpose methods.
    - Faster convergence rate compared to Steepest Descent and only requires evaluation of objective function and it's gradient - no matrix operations.

**Disadvantages**:
    - For Fletcher-Reeves method it can be shown that if the method generates a bad direction and step, then the next direction and step are also likely to be bad. However, this is not the case with the Polak Ribiere method.
    - Generally, the Polak Ribiere method is more efficient that the Fletcher-Reeves method but it has the disadvantage is requiring one more vector of storage.

[Nocedal]_

.. _bfgs:

BFGS (``bfgs``)
***************
Most popular quasi-Newton method, which uses an approximate Hessian rather than the true Hessian which is used in a Newton line search method.

Starting with an initial Hessian approximation :math:`H_0` and starting point :math:`x_0`:

While :math:`\| \nabla f_k \| > \epsilon`:

Compute the search direction :math:`p_k = -H_k \nabla f_k`

Then find next iterate :math:`x_{k+1}` by performing a line search.

Next, define :math:`s_k = x_{k+1}-x_k` and :math:`y_k = \nabla f_{k+1} - \nabla f_k`, then compute

.. math::
    H_{k+1} = (I - \rho_k s_k y_k^T)H_k(I - \rho_k y_k s_K^T) + \rho_k s_k s_k^T

with :math:`\rho_k = \frac{1}{y_k^T s_k}`

**Advantages**:
    - Superlinear rate of convergence
    - Has self-correcting properties - if there is a bad estimate for :math:`H_k`, then it will tend to correct itself within a few iterations.
    - No need to compute the Jacobian or Hessian.

**Disadvantages**:
    - Newton's method has quadratic convergence but this is lost with BFGS.

[Nocedal]_

.. _gauss_newton:

Gauss Newton (``gauss_newton``)
*******************************
Modified Newton's method with line search. Instead of solving standard Newton equations

.. math::
    \nabla^2 f(x_k)p = -\nabla f(x_k), solve the system

.. math::
    J_k^T J_k p_k^{GN} = - J_k^T r_k

(where :math:`J_k` is the Jacobian) to obtain the search direction :math:`p_k^{GN}`. The next iterate is then set as :math:`x_{k+1} = x_k + p_k^{GN}`.

Here, the approximation of the Hessian :math:`\nabla^2 f_k \approx J_k^T J_k` has been made, which helps to save on computation time as second derivatives are not calculated.

**Advantages**:
    - Calculation of second derivatives is not required.
    - If residuals or their second order partial derivatives are small, then :math:`J_k^T J_k` is a close approximation to :math:`\nabla^2 f_k` and convergence of Gauss-Newton is fast.
    - The search direction :math:`p_J^{GN}` is always a descent direction as long as :math:`J_k` has full rank and the gradient :math:`\nabla f_k` is nonzero.

**Disadvantages**:
    - Without a good initial guess, or if the matrix :math:`J_k^T J_k` is ill-conditioned, the Gauss Newton Algorithm is very slow to converge to a solution.
    - If relative residuals are large, then large amounts of information will be lost.
    - :math:`J_k` must be full rank.

[Nocedal]_ [Floater]_

.. [Nocedal] Jorge Nocedal, Stephen J. Wright (2006), Numerical Optimization

.. [Poczos] Barnabas Poczos, Ryan Tibshirani (2012), Lecture 10: Optimization, School of Computer Science, Carnegie Mellon University

.. [Floater] Michael S. Floater (2018), Lecture 13: Non-linear least squares and the Gauss-Newton method, University of Oslo
