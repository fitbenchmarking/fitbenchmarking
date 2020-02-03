.. _local_min:

#####################
Local Minimiser Table
#####################

The local min results shows a ``True`` or ``False`` value together with a number. The ``True`` or ``False`` indicates whether the software finds a minimum with respect to the following criteria:

    - :math:`||r|| \leq \mbox{RES\_TOL}`,
    - :math:`|| J^T r|| \leq \mbox{GRAD\_TOL}`,
    - :math:`\frac{|| J^T r||}{||r||} \leq \mbox{GRAD\_TOL}`,

where :math:`J` and :math:`r` are the Jacobian and residual of :math:`f(x, p)`, respectively. The tolerances can be found in the results object.

