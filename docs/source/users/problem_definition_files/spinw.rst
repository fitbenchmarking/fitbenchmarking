.. _spinw_format:

*****************
SpinW File Format
*****************

The SpinW file format is based on :ref:`native`, this page is intended to
demonstrate where the format differs.

As in the native format, an input file must start with a comment indicating
that it is a FitBenchmarking problem followed by a number of key value pairs.
Available keys can be seen in :ref:`native` and below:

software, name, description
  As described in the native format.

input_file
  For SpinW we require an SQW file containing the data from Horace.

projection
  The projection defines the axis that the data is projected onto for the fit.

  This follows a similar pattern to the function in that it is a comma
  seperated list of key-value pairs and has several parameters.
  Usually only u, v, and type are used.
  - u, v, and w: 3D vectors used to define the viewing coordinate system.
                 w will be defined as normal to the plane spanned by u and v
                 if not given.
  - type: 3 chars (a, r, or p) to define the type of axes.
          a - The axis is measured in angstroms,
          r - The axis is measured in rlu (scaled so the 1-norm == 1),
          p - The axis is not altered (preserve values)
  - uoffset: 4D vector, if the data needs recentreing this can be used
  
  Vectors can be defined as comma seperated values in square brackets
  `[val1, val2, ...]`

  e.g.::
    projection = 'u=[1,0,0],v=[0,1,0],type=rrr'

cut
  The cut defines the extent of the data and consists of 4 ranges for binning
  boundaries.
  Each range can be defined by:
  - no value: Keep the data as stored in the file
  - single value: Sets a bin width, the data is rebinned into this width
  - 3 values => lower bound, bin width, upper bound. The data is truncated and rebinned.
  - 2 values => lower and upper bound. The data is truncated into a single bin.

  e.g.::
    cut = 'p1_bin=[-1,0.05,1],p2_bin=[-1,0.05,1],p3_bin=[-10,10],p4_bin=[10,20]'

sample
  The sample defines the target of the experiment and has several parameters.

  This must have a class as "IX_Sample", the remaining arguments are passed
  through to the IX_Sample class constructor.
  Full details can be found `here <https://pace-neutrons.github.io/Horace/v3.6.2/user_guide/Resolution_convolution.html#the-tobyfit-class>`__.
  
  e.g.::
    sample = 'class=IX_sample,xgeom=[0,0,1],ygeom=[0,1,0],shape='cuboid',ps=[0.01,0.05,0.01])

instrument
  The instrument defines where the measurements were taken and again requires
  a ``class`` followed by the correct arguments for the class.

  As with sample, details can be found `here <https://pace-neutrons.github.io/Horace/v3.6.2/user_guide/Resolution_convolution.html#the-tobyfit-class>`__.
  
  e.g.::
    instrument = 'class=maps_instrument,ei=70,hz=250,chopper=S'

function
  The function is defined by a matlab file which returns a SpinW model.

  The format is again comma seperated key-value pairs, with the matlab file
  defined by the variable "matlab_script" and the remaining pairs defining starting
  values as in the native parser.

  e.g.::
    function = 'matlab_script=pcsmo_model.m,J=35,D=0,gam=30,temp=10,amp=300'

random_fraction_pixels
  SpinW problems can be very large. This option will mask out a proportion of
  pixels to reduce the problem size.

  The following example retains only 1% of the data.

  e.g.::
    random_fraction_pixels = 0.01

mc_points
  SpinW used Monte Carlo sampling during it's calculation. This controls the
  number of samples taken. It is left to the experienced SpinW user to tune
  this.

  e.g.::
    mc_points = 5

intrinsic_energy_width
  Each call to SpinW also requires an energy width. This parameter is not
  fitted.

  e.g.::
    intrinsic_energy_width = 0.1

spinwpars
  SpinW models have some additional parameters which are passed to TobyFit.
  These can be set for the model by adding them to the file as a new value
  prefixed with "spinwpars_".

  It is left to the experienced SpinW user to know what their problem requires
  in this regard.

  Some examples might be:
  - spinwpars_mat = ['JF1', 'JA', 'JF2', 'JF3', 'Jperp', 'D(3,3)']
  - spinwpars_hermit = False
  - spinwpars_optmem = 1
  - spinwpars_useFast = False
  - spinwpars_... = ...
