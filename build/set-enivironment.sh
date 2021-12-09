# Set up the environment variables needed for third party
# software to work

HERE=${PWD}

export VIRTUAL_ENV=${HERE}/venv
export PATH="$VIRTUAL_ENV/bin:$PATH"
# RALfit
export LD_LIBRARY_PATH=${HERE}/RALFit/libRALFit/build/src:$LD_LIBRARY_PATH
# CUTEST
CUTEST_DIR=${HERE}/cutest
export ARCHDEFS=${CUTEST_DIR}/archdefs/ 
export SIFDECODE=${CUTEST_DIR}/sifdecode/
export MASTSIF=${HERE}/fitbenchmarking/examples/benchmark_problems/SIF/ 
export CUTEST=${CUTEST_DIR}/cutest/ 
export MYARCH="pc64.lnx.gfo" 
export PYCUTEST_CACHE=${CUTEST_DIR}/pycutest_cache/
export PYTHONPATH="${PYCUTEST_CACHE}:${PYTHONPATH}"
# Mantid
export PYTHONPATH=$PYTHONPATH:${HERE}/Mantid/lib:${HERE}/Mantid/bin
export HDF5_DISABLE_VERSION_CHECK=2
python3 -m venv $VIRTUAL_ENV
# Matlab
export PATH="$PATH:${HERE}/Matlab/R2021a/bin"
