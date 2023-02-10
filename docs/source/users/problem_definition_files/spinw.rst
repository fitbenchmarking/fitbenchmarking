.. _spinw_format:

*****************
SpinW File Format
*****************

The SpinW file format is based on :ref:`native`, this page is intended to
demonstrate where the format differs.

Examples of spinw problems are:

.. literalinclude:: ../../../../examples/benchmark_problems/SpinW/test1.txt

.. literalinclude:: ../../../../examples/benchmark_problems/SpinW/test6.txt

.. literalinclude:: ../../../../examples/benchmark_problems/SpinW/test10.txt

.. note::
The SpinW file format requires you to have ran the benchmark problem in Horace 
using :code:`fit()` and :code:`simulate()` successfully. Here are some relevant links on 
how to run `Multifit <https://pace-neutrons.github.io/Horace/unstable/manual/Multifit.html/>`__ ,
`Advanced Multifit <https://pace-neutrons.github.io/Horace/unstable/manual
/Advanced_Multifit.html/>`__ 
and `Tobyfit <https://pace-neutrons.github.io/Horace/unstable/manual/Tobyfit.html/>`__ problems and 
`Running Horace in Parallel <https://pace-neutrons.github.io/Horace/unstable/manual/Parallel.html/>`__.

As in the native format, an input file must start with a comment indicating
that it is a FitBenchmarking problem followed by a number of key value pairs.
Available keys can be seen in :ref:`native` and below:

software, name, description
  As described in the native format.

input_file
  For SpinW we require an SQW file containing the data from Horace.

function
  The function is defined by a matlab file which returns a SpinW model.

  The format is again comma seperated key-value pairs, with the matlab file
  defined by the variable "matlab_script" and the remaining pairs defining starting
  values as in the native parser.

wye_function
  The wye_function is defined by a matlab file which returns the w (This could be a sqw ,d1d, d2d, d3d and d4d object), y (signal),
  e (standard deviation) and the msk (This is a n dimensional array which is the same shape as y and e of the pixels used for the fitting).
  This matlab file takes in the path of the datafile and the path of where the matlab functions are located.

  Explained example of the wye_function:

  The first three lines adds the path to matlab functions need for fitting and loads the w object.

  .. code-block:: rst

    addpath(genpath(path));
    source_data = load(datafile);
    w = source_data.w1 ;

  The next line gets the y and e from the w object. These are the true y and e values from the experiment.    

  .. code-block:: rst
    
    [spinw_y, spinw_e] = sigvar_get(w);

  The next block of run :code:`simulate()` once for the sole purpose of getting the msk array 
  
  .. code-block:: rst
    
    pin=[100,50,7,0,0];
    forefunc = @mftest_gauss_bkgd;
    mf = multifit(w);
    mf = mf.set_fun(forefunc);
    mf = mf.set_pin (pin);
    [wout,fitpar] = mf.simulate();
    [ ~, ~, msk] = sigvar_get(wout);
  
  The last two lines of the wye_function applies the msk on the y and e data. As the e from Horace is the
  variance we have squared root the value to get the standard deviation.

  .. code-block:: rst

    y = spinw_y(msk);
    e = sqrt(spinw_e(msk));

  Example of the wye_function:

  .. literalinclude:: ../../../../examples/benchmark_problems/SpinW/m_scripts/wye_functions/fb_wye_IX_1D_test1.m

simulate_function
  The simulate_function is defined by a matlab file which returns the y values for the fitting function.
  This matlab file takes in the w, fitpars (fitting parameters) and msk. The w and msk are the same as the 
  wye_function. The fitpars are are determined by the current minimizer.  

Explained Example of the simulate_function:

.. code-block:: rst
  
  forefunc = @mftest_gauss_bkgd;
  mf = multifit(w);
  mf = mf.set_fun(forefunc);
  mf = mf.set_pin(fitpars);
  [wout,fitpar] = mf.simulate();
  [spinw_y, e] = sigvar_get(wout);
  spinw_y=spinw_y(msk);

.. note:: 
  If the benchmark problem is `tobyfit` or using monte carlo. A persisent seed needs to be set before simulate is ran.
  This make sure that it uses the same seed everytime :code:`simulate()`  is ran.  
    
  .. code-block:: rst

    persistent seed
    if isempty (seed)
        rng(3,"twister");
        seed = rng();
    else 
        rng(seed);
    end

.. note:: 
  If the SpinW benchmark problem is run in parallel make sure to turn off hpc after :code:`simulate()` in the simulate_function 
  matlab script. 

  .. code-block:: rst

    hpc('off')


Example of thw simulate_function:
  
.. literalinclude:: ../../../../examples/benchmark_problems/SpinW/matlab_script=m_scripts/simulate_functions/fb_simulate_IX_1D_test1.m

spinw_path
  The spinw_path is the path where all matlab functions used in the fitting are located 
  (i.e simulate_function, wye_function,mftest_gauss_bkgd etc).

.. note:: 
  If you have a non standard installation of Horace please set the `HORACE_LOCATION` and the `SPINW_LOCATION`
  as environment variables(i.e on IDAaaS).  
