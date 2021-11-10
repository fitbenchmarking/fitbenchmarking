# First, let's setup the basics
sudo apt-get update
sudo apt-get install -y \
     python3 \
     python3-pip \
     python3-dev \
	python3-venv \
	git \
	sudo \
	cmake

HERE=${PWD}

VENV_DIR=${HERE}/venv
mkdir VENV_DIR
export VIRTUAL_ENV=VENV_DIR
python3 -m venv $VIRTUAL_ENV
export PATH="$VIRTUAL_ENV/bin:$PATH"

pip install wheel
pip install pytest>3.6 \
            pytest-cov \
	    coveralls \
	    coverage~=4.5.4 \
            urllib3==1.23 \
	    mock

# Install pygsl
sudo apt-get install -y gsl-bin libgsl-dev libgsl-dbg

# Install RALFit
sudo apt-get install -y gfortran lcov libblas-dev liblapack-dev ligdal-dev
git clone https://github.com/ralna/RALFit
pip install numpy
mkdir -p ${HERE}/RALFit/libRALFit/build
cd ${HERE}/RALFit/libRALFit/build
cmake .. && make && make install
pip install .
export LD_LIBRARY_PATH=/RALFit/libRALFit/build/src:$LD_LIBRARY_PATH

# Install  cutest
CUTEST_DIR=${HERE}/cutest
mkdir -p ${CUTEST_DIR}
cd ${CUTEST_DIR}
git clone https://github.com/ralna/ARCHDefs ./archdefs 
git clone https://github.com/ralna/SIFDecode ./sifdecode 
git clone https://github.com/ralna/CUTEst ./cutest
mkdir pycutest_cache
export ARCHDEFS=${CUTEST_DIR}/archdefs/ 
export SIFDECODE=${CUTEST_DIR}/sifdecode/
export MASTSIF=${HERE}/fitbenchmarking/examples/benchmark_problems/SIF/ 
export CUTEST=${CUTEST_DIR}/cutest/ 
export MYARCH="pc64.lnx.gfo" 
export PYCUTEST_CACHE=${CUTEST_DIR}/pycutest_cache/
export PYTHONPATH="${PYCUTEST_CACHE}:${PYTHONPATH}"
cd $SIFDECODE
printf "6\n2\n6\n" > sifdecode.input 
printf "nny" >> sifdecode.input
./install_sifdecode  < sifdecode.input
cd  $CUTEST
printf "6\n2\n6\n2\n8\n" > cutest.input
printf "nnydn" >> cutest.input
./install_cutest < cutest.input
python -m pip install pycutest

# Install mantid
