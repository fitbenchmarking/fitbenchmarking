acc: Start

The accuracy results are calculated from the final chi squared value:

.. math:: \min_p \sum_{i=1}^n \left( \frac{y_i - f(x_i, p)}{e_i} \right)^2

where :math:`n` data points :math:`(x_i,y_i)`, associated errors :math:`e_i`, and a model function :math:`f(x,p)`.

acc: End

compare: Start

The combined results show the accuracy in the first line of the cell and the runtime on the second line of the cell.

compare: End

local_min: Start

The local min results shows a ``True`` or ``False`` value together with :math:`\frac{|| J^T r||}{||r||}`. The ``True`` or ``False`` indicates whether the software finds a minimum with respect to the following criteria:


- :math:`||r|| \leq \mbox{RES\_TOL}`,
- :math:`|| J^T r|| \leq \mbox{GRAD\_TOL}`,
- :math:`\frac{|| J^T r||}{||r||} \leq \mbox{GRAD\_TOL}`,

where :math:`J` and :math:`r` are the Jacobian and residual of :math:`f(x, p)`, respectively. The tolerances can be found in the results object.

local_min: End

runtime: Start

The timing results are calculated from an average using the `timeit <https://docs.python.org/2/library/timeit.html>`_  module in python. The number of runs can be set in :ref:`options`.

runtime: End

abs: Start

Absolute values are displayed in the table.

abs: End

rel: Start

Relative values are displayed in the table.

rel: End

both: Start

Absolute and relative values are displayed in the table in the format: ``abs (rel)``, for example ``5.1 (1)`` where 5.1 is abs and 1 is rel values respectively

both: End
