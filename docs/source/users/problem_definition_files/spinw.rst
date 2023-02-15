.. _spinw_format:

*****************
SpinW File Format
*****************

The SpinW file format is based on :ref:`native`, this page is intended to
demonstrate where the format differs.

Examples of spinw problems are:

.. literalinclude:: ../../../../examples/benchmark_problems/SpinW/1D_Gaussian_1.txt

.. literalinclude:: ../../../../examples/benchmark_problems/SpinW/3D_Gaussian.txt

.. literalinclude:: ../../../../examples/benchmark_problems/SpinW/PCSMO_at_001_data.txt

.. note::
The SpinW file format requires you to have run the benchmark problem in Horace 
using :code:`fit()` and :code:`simulate()` successfully. Relevant links on 
how to run this are: `Multifit <https://pace-neutrons.github.io/Horace/unstable/manual/Multifit.html>`__ ,
`Advanced Multifit <https://pace-neutrons.github.io/Horace/unstable/manual
/Advanced_Multifit.html>`__ 
and `Tobyfit <https://pace-neutrons.github.io/Horace/unstable/manual/Tobyfit.html>`__ problems as well as 
`Running Horace in Parallel <https://pace-neutrons.github.io/Horace/unstable/manual/Parallel.html>`__.

As in the native format, an input file must start with a comment indicating
that it is a FitBenchmarking problem followed by a number of key value pairs.
Available keys can be seen in :ref:`native` and below:

software, name, description
  As described in the native format.

input_file
  For SpinW we require a ``.sqw`` or ``.mat`` file containing preprocessed, Horace-compatible data. 
  
.. note::
  The ``.mat`` file is the result of using `save(file, sqw_objects) <https://uk.mathworks.com/help/matlab/ref/save.html>`__ 
  and should be used if you are loading in multiple ``sqw`` objects. Make sure 
  to load the data in appropriately in the `wye_function`. 

function
  The function is defined by one or more matlab script (``.m``) files which return a model of the foreground or foreground and background
  respectively.

  The format for defining the function is based on comma-separated key-value pairs, where the Matlab script files 
  are defined by the variables "foreground" and "background". The remaining pairs define the starting values for 
  each of the models, respectively. It's important to note that these pairs must be defined after their respective models.

  If both the foreground and background models are defined, they should be given as a semicolon-separated list. In this 
  case, there would be two comma-separated key-value pairs, one for the foreground and foreground parameters, and 
  another for the background and background parameters, separated by a semicolon.    

  Examples:

    Only foreground: 
    
    .. code-block:: rst

      function = 'foreground=m_scripts/functions/mftest_gauss_bkgd.m ,height=100,centre=50,sigma=7,const=0,grad=0'

    Foreground and background:

    .. code-block:: rst

      function = 'foreground=m_scripts/functions/gauss.m ,height=1100,centre=66 ,stdev=13; background=m_scripts/functions/linear_bg.m ,bkgd_const=15'

  
wye_function
    The wye_function is defined by a matlab file which returns the: 

    `w` 
        an ``sqw`` , ``dnd``, ``ix_dataset`` object or ``xye`` struct. (see `Multifit <https://pace-neutrons.github.io/Horace/unstable/manual/Multifit.html>`__)
    `e` 
        standard deviation data
    `y` 
        intensity data
        
    `msk`
        logical mask array of which elements are to be retained
    
This function takes the path to the datafile and the path to the matlab functions as arguments.

  Explained example of the wye_function:

   The first three lines add the path to matlab functions needed for fitting and loads the `w` object.

  .. code-block:: matlab

    addpath(genpath(path));
    source_data = load(datafile);
    w = source_data.w1 ;

  The next line gets the y and e from the `w` object. These are the true `y`, `e` and `msk` values from the experiment.    

  .. code-block:: matlab
    
    [spinw_y, spinw_e, msk] = sigvar_get(w);

  Any elements in msk that have a corresponding element in spinw_y that is equal to zero will be set to zero.
  The purpose of this is to exclude these elements from subsequent calculations, since they are not informative.  
  
  .. code-block:: matlab
    
    msk(spinw_y==0) = 0;
  
  The last two lines of the wye_function applies the `msk` to the `y` and `e` data. As the `e` from retrieved above is the
  variance we have taken the square root of the value to get the standard deviation.

  .. code-block:: matlab

    y = spinw_y(msk);
    e = sqrt(spinw_e(msk));

  Examples of the wye_function:

  .. literalinclude:: ../../../../examples/benchmark_problems/SpinW/m_scripts/wye_functions/fb_wye_IX_1D_test1.m
  
  .. literalinclude:: ../../../../examples/benchmark_problems/SpinW/m_scripts/wye_functions/fb_wye_pcsmo_test.m

simulate_function
  The simulate_function is defined by a matlab file which returns the derived y values from `simulate()` for the fitting function.
  This matlab file takes in the `w`, `fitpars` (fitting parameters) and `msk`. The `w` and `msk` are the same as the 
  wye_function. The `fitpars` are determined by the current minimizer.  

Explained Example of the simulate_function:

.. code-block:: matlab
  
  forefunc = @mftest_gauss_bkgd;
  mf = multifit(w);
  mf = mf.set_fun(forefunc);
  mf = mf.set_pin(fitpars);
  [wout,fitpar] = mf.simulate();
  [spinw_y, e] = sigvar_get(wout);
  spinw_y=spinw_y(msk);

.. note:: 
  If the benchmark problem uses random numbers in any way (e.g. `tobyfit`).
  A persisent seed needs to be set before simulate is run.  
  This make sure that it uses the same seed everytime :code:`simulate()` is ran.  
    
  .. code-block:: matlab

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

  .. code-block:: matlab

    hpc('off')


Examples of the simulate_function:
  
.. literalinclude:: ../../../../examples/benchmark_problems/SpinW/m_scripts/simulate_functions/fb_simulate_IX_1D_test1.m

.. literalinclude:: ../../../../examples/benchmark_problems/SpinW/m_scripts/simulate_functions/fb_simulate_pcsmo_test.m

.. note::
   All the functions needed in the fitting must be in the subdirectory of the benchmark problem.

.. note:: 
  If you have a non standard installation of Horace please set the `HORACE_LOCATION` and the `SPINW_LOCATION`
  as environment variables(e.g on IDAaaS).  
