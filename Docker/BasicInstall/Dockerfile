# Use ubuntu as a parent image
FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

# Install the packages we need to build fitbenchmarking
RUN apt-get update && apt-get install -y \
    git \
    sudo \
    cmake \
    mpich

# use uv to manage python version
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
RUN uv python install 3.12

# set up a venv to stop python/python3 sillyness
ENV VIRTUAL_ENV=/opt/venv
RUN uv venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install wheel
RUN pip install "pytest>3.6" \
    pytest-cov \
    coveralls \
    "coverage~=4.5.4" \ 
    "urllib3==1.23" \
    mock 

WORKDIR /home/



