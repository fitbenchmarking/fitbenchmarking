.. _local_min:

#####################
Local Minimiser Table
#####################

The local min results show a ``True`` or ``False`` values together with a number. The ``True`` or ``False`` indicates whether the software finds a minimum with respect to the following criteria:

    - :math:`||r|| \leq RES\_TOL`,
    - :math:`|| J^T r|| \leq GRAD\_TOL`,
    - :math:`\frac{|| J^T r||}{||r||} \leq GRAD\_TOL`,

where :math:`J` and :math:`r` is the Jacobian and residual, respectively. The tolerances can be found in the results object.
