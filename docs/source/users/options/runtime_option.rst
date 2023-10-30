.. _runtime_option:

###############
Runtime Options
###############

The runtime section explains the metrics available for benchmarking the runtime performance.

1) Mean
-------

This is the default option for benchmarking runtime. If no argument is passed to the ``-rt`` flag from the **cli**, then
the average runtime of *n* iterations would be represented on the frontend. It can however also be set explicitly by passing
``mean`` argument to the ``-rt`` flag from the **cli**

.. math::

   \overline{r} = \frac{1}{n} \sum_{i=1}^n x_i = \frac{{x_1}+{x_2}....+{x_n}}{n} \label{1} \tag{1}

2) Minimum
----------

This option can be selected by passing ``minimum`` argument to the ``-rt`` flag from the **cli**. This
will choose the lowest runtime of *n* iterations to be represented on the frontend. 

.. math::

   runtime = \min[{x_1},....,{x_n}]

3) Maximum
----------

This option can be selected by passing ``maximum`` argument to the ``-rt`` flag from the **cli**. This
will choose the highest runtime of *n* iterations to be represented on the frontend. 

.. math::

   runtime = \max[{x_1},....,{x_n}]


4) First
--------

This option can be selected by passing ``first`` argument to the ``-rt`` flag from the **cli**. This
will choose the first runtime of *n* iterations to be represented on the frontend. 

.. math::

   runtime = {x_1}

5) Median
---------

This option can be selected by passing ``median`` argument to the ``-rt`` flag from the **cli**. This
will calculate the median runtime of *n* iterations. 

.. math::

   runtime =  \begin{cases}
         {x_\frac{n+1}{2}} &\text{if n is odd}  \\
         \frac {{x_\frac{n}{2}}+{x_\frac{n+2}{2}}}{2} &\text{if n is even}    \\
   \end{cases}

where :math:`runtimes = [{x_1} \leq {x_2} \leq ... \leq {x_n}]` .

6) Harmonic
-----------

This option can be selected by passing ``harmonic`` argument to the ``-rt`` flag from the **cli**. This
will calculate the harmonic mean of *n* iterations and display it on the frontend. 

.. math::

   runtime = \frac{n}{ \sum_{i=1}^n \frac{1}{x_i}}
    = \frac{n}{\frac{1}{x_1}+\frac{1}{x_2}+ ... + \frac{1}{x_n}} \quad \Big\vert \quad 0 \notin [{x_1}, {x_2}, ... ,{x_n}]

.. note::
   Mathematically none of the values should be zero as taking an inverse 
   is an intermediary step when calculating the harmonic mean. However, the ``harmonic_mean``
   funtion from the ``statistics`` library will handle the zero values in the input without throwing
   a ``ZeroDivisionError``.

7) Trim mean
------------

This option can be selected by passing ``trim`` argument to the ``-rt`` flag from the **cli**. This
will calculate the trimmed mean of *n* iterations and display it on the frontend. The trimmed mean is 
calculated using the following steps.

1) Order the runtime results :math:`[{x_1} \leq {x_2} \leq ... \leq {x_n}]`
2) Remove 20% of the lowest and highest runtimes.
3) Calculate the arithmetic mean of remaining runtimes using Equation :math:`\ref{1}` .
