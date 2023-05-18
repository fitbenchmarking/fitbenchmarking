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
export VIRTUAL_ENV=$VENV_DIR
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
sudo apt-get install -y gfortran lcov libblas-dev liblapack-dev libgdal-dev
git clone https://github.com/ralna/RALFit
pip install numpy
mkdir -p ${HERE}/RALFit/libRALFit/build
cd ${HERE}/RALFit/libRALFit/build
cmake .. && make && make install
pip install .
export LD_LIBRARY_PATH=${HERE}/RALFit/libRALFit/build/src:$LD_LIBRARY_PATH

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
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/jfowkes/pycutest/master/.install_cutest.sh)"
pip install pycutest

# Install mantid
cd $HERE
# set noninteractive to stop tzdata prompt
export DEBIAN_FRONTEND=noniteractive
OLD_VENV=$VIRTUAL_ENV
export VIRTUAL_ENV=""
export OLD_PATH=$PATH
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
sudo apt-get install -y git g++ qt5-default clang-format-6.0 cmake dvipng doxygen libtbb-dev \
  libgoogle-perftools-dev libboost-all-dev libpoco-dev libnexus-dev libhdf5-dev libhdf4-dev \
  libjemalloc-dev libgsl-dev liboce-visualization-dev libmuparser-dev libssl-dev libjsoncpp-dev \
  librdkafka-dev qtbase5-dev qttools5-dev qttools5-dev-tools libqt5webkit5-dev \
  libqt5x11extras5-dev libqt5opengl5-dev libqscintilla2-qt5-dev libpython3-dev \
  ninja-build python3-setuptools python3-sip-dev python3-pyqt5 pyqt5-dev pyqt5-dev-tools \
  python3-qtpy python3-numpy python3-scipy python3-sphinx python3-sphinx-bootstrap-theme \
  python3-pycifrw python3-dateutil python3-matplotlib python3-qtconsole python3-h5py \
  python3-mock python3-psutil python3-requests python3-toml python3-yaml wget

# Details from mantid website
wget https://downloads.sourceforge.net/project/mantid/6.3/mantid-6.3.0-Source.tar.xz
tar -xvf mantid-6.3.0-Source.tar.xz
rm mantid*.xz

sudo apt-get install -y ccache
ccache --max-size=20G

mkdir -p Mantid

cd Mantid
cmake ${HERE}/mantid-6.3.0-Source -DENABLE_MANTIDPLOT=OFF
make

export VIRTUAL_ENV=$OLD_VENV
export PATH=$OLD_PATH
unset OLD_PATH
export PYTHONPATH=$PYTHONPATH:${HERE}/Mantid/lib:${HERE}/Mantid/bin
pip install IPython six python-dateutil pyyaml h5py
export HDF5_DISABLE_VERSION_CHECK=2
${HERE}/Mantid/bin/mantidpython -m  mantid.simpleapi || echo "expected segfault on first run"

cd $HERE

# setup pygsl
pip install pygsl
