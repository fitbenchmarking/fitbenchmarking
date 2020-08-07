# Use ubuntu as a parent image
FROM ubuntu:18.04

# Install the packages we need to have to build fitbenchmarking
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    git 

# set up a venv to stop python/python3 sillyness
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install the things needed for gsl
RUN apt-get install -y gsl-bin \
 libgsl-dev \
 libgsl-dbg

# Install RALFit
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

# Build cutest
