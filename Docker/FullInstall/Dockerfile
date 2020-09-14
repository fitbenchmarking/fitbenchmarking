# Use the basic dependencies
FROM fitbenchmarking/fitbenchmarking-deps:latest

WORKDIR /

#################
# Install pygsl #
#################

RUN apt-get update && \
 apt-get install -y gsl-bin \
 libgsl-dev \
 libgsl-dbg

##################
# Install RALFit #
##################
RUN apt-get install -y gfortran \
    lcov \
    libblas-dev \
    liblapack-dev \
    cmake \
    libgdal-dev

RUN git clone https://github.com/ralna/RALFit

RUN pip install numpy

RUN mkdir -p /RALFit/libRALFit/build

WORKDIR /RALFit/libRALFit/build

RUN cmake .. && make && make install

# make install for RALFit doesn't work on docker, so manually pip install
RUN pip install .

ENV LD_LIBRARY_PATH=/RALFit/libRALFit/build/src:$LD_LIBRARY_PATH

################
# Build cutest #
################

RUN mkdir -p /cutest

WORKDIR /cutest

RUN git clone https://github.com/ralna/ARCHDefs ./archdefs && \
    git clone https://github.com/ralna/SIFDecode ./sifdecode && \
    git clone https://github.com/ralna/CUTEst ./cutest

RUN mkdir pycutest_cache

ENV ARCHDEFS=/cutest/archdefs/ \
    SIFDECODE=/cutest/sifdecode/ \
    MASTSIF=/home/fitbenchmarking/examples/benchmark_problems/SIF/ \
    CUTEST=/cutest/cutest/ \
    MYARCH="pc64.lnx.gfo" \
    PYCUTEST_CACHE=/cutest/pycutest_cache/

ENV PYTHONPATH="${PYCUTEST_CACHE}:${PYTHONPATH}"

# Install sifdecode

WORKDIR $SIFDECODE
RUN printf "6\n2\n6\n" > sifdecode.input && \
    printf "nny" >> sifdecode.input && \
    ./install_sifdecode  < sifdecode.input

# Install cutest
WORKDIR $CUTEST
RUN printf "6\n2\n6\n2\n8\n" > cutest.input && \
    printf "nnydn" >> cutest.input && \
    ./install_cutest < cutest.input

# install pycutest
RUN python -m pip install pycutest

##################
# Install Mantid #
##################

# set noninteractive to stop tzdata prompt
ENV DEBIAN_FRONTEND=noniteractive

RUN apt-get install -y --fix-missing wget \
                       lsb-release \ 
		       software-properties-common
RUN wget -O - http://apt.isis.rl.ac.uk/2E10C193726B7213.asc -q | apt-key add -
RUN apt-add-repository "deb [arch=amd64] http://apt.isis.rl.ac.uk $(lsb_release -c | cut -f 2) main" -y 
RUN apt-add-repository ppa:mantid/mantid -y
RUN apt-get update && apt-get install mantid -y

ENV PYTHONPATH=$PYTHONPATH:/opt/Mantid/lib:/opt/Mantid/bin
RUN pip install IPython six
RUN /opt/Mantid/bin/mantidpython -m  mantid.simpleapi || echo "expected segfault on first run"

#################
# install pygsl #
#################
RUN python -m pip install pygsl


## ALL SET UP ##
WORKDIR /home/